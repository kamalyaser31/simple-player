import time as stdlib_time
import threading
import types
import unittest
from unittest import mock

from playlist.state import PlaylistState
from youtube import flow
from youtube.components import CancelFlag
from youtube.resolver import YtItem
from youtube.state import mk_ses
from youtube.task_ui import TaskOut


class Settings:
    def get_yt_audio_only(self):
        return True

    def get_yt_video_quality(self):
        return "medium"

    def get_yt_prefetch_count(self):
        return 0


class PlaylistPlayer:
    def __init__(self, current_item, next_item):
        self.state = PlaylistState()
        self.state.open_file("current-stream", source=current_item.url)
        self.state.append("stale-stream", source=next_item.url)

    @property
    def current_source(self):
        return self.state.current_source

    def has_source(self, source):
        return self.state.has_source(source)

    def replace_queued_stream(self, url, source_url):
        return self.state.replace_queued_source_path(source_url, url)

    def replace_current_stream(self, url, source_url):
        if self.current_source != source_url:
            return False
        return self.state.replace_path(self.state.current_path, url)

    def queue_stream(self, url, title=None, source_url=None):
        return self.state.append(url, title=title, source=source_url)

    def next_track(self):
        return self.state.next_track(use_shuffle=True, wrap=False)


class Context:
    def __init__(self, player):
        self.player = player
        self.settings = Settings()
        self.frame = object()
        self.yt_pl = None
        self.yt_now = {"title": "Test", "desc": ""}
        self.yt_retry_source = None


def video(name):
    return YtItem(
        title=name,
        url=f"https://youtube.com/watch?v={name}",
        channel_url="",
        channel_name="",
        description="",
    )


class YouTubeRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.cache = dict(flow._PREP_DONE)
        self.futures = dict(flow._PREP_FUT)
        self.shutting_down = flow._SHUTTING_DOWN
        flow._PREP_DONE.clear()
        flow._PREP_FUT.clear()
        flow._SHUTTING_DOWN = False

    def tearDown(self):
        flow._PREP_DONE.clear()
        flow._PREP_DONE.update(self.cache)
        flow._PREP_FUT.clear()
        flow._PREP_FUT.update(self.futures)
        flow._SHUTTING_DOWN = self.shutting_down

    def test_cache_expires_without_mutating_stdlib_clock(self):
        original_monotonic = stdlib_time.monotonic
        clock = {"now": 10.0}
        fake_time = types.SimpleNamespace(monotonic=lambda: clock["now"])

        with mock.patch.object(flow, "time", fake_time):
            flow._cache_set("key", {"stream": "url"})
            self.assertEqual(flow._cache_get("key"), {"stream": "url"})
            clock["now"] += flow._PREP_TTL
            self.assertIsNone(flow._cache_get("key"))

        self.assertIs(stdlib_time.monotonic, original_monotonic)

    def test_fresh_resolution_replaces_stale_queued_stream(self):
        current_item = video("current")
        next_item = video("next")
        player = PlaylistPlayer(current_item, next_item)
        context = Context(player)
        session = mk_ses("playlist", "Test", [current_item, next_item])
        session["queued"].add(next_item.url)
        context.yt_pl = session
        key = flow._prep_key(next_item.url, flow._opts(context, session))
        flow._cache_set(key, {"item": next_item, "stream": "fresh-stream"})

        self.assertTrue(flow.try_next(context))
        self.assertEqual(player.state.current_path, "fresh-stream")
        self.assertEqual(
            player.state.get_file_list(), ["current-stream", "fresh-stream"]
        )

    def test_playback_error_retries_once_after_cache_expiry(self):
        current_item = video("expired")
        player = PlaylistPlayer(current_item, video("next"))
        context = Context(player)

        def run_synchronously(_parent, _title, job, **_kwargs):
            value = job(CancelFlag(), lambda _line: None, lambda _update: None)
            return TaskOut(ok=True, val=value)

        with mock.patch.object(
            flow.wx,
            "CallAfter",
            side_effect=lambda callback, *args: callback(*args),
        ), mock.patch.object(
            flow, "run_task", side_effect=run_synchronously
        ), mock.patch.object(
            flow,
            "fetch_play",
            return_value={"item": current_item, "stream": "fresh-stream"},
        ) as fetch_play:
            self.assertTrue(flow.on_playback_finished(context, reason=4))
            self.assertFalse(flow.on_playback_finished(context, reason=4))

        self.assertEqual(player.state.current_path, "fresh-stream")
        self.assertEqual(fetch_play.call_count, 1)

    def test_evicted_prefetch_cannot_overwrite_fresh_retry(self):
        current_item = video("current")
        next_item = video("race")
        player = PlaylistPlayer(current_item, next_item)
        context = Context(player)
        session = mk_ses("playlist", "Test", [current_item, next_item])
        session["queued"].add(next_item.url)
        context.yt_pl = session
        options = flow._opts(context, session)
        key = flow._prep_key(next_item.url, options)
        started = threading.Event()
        release = threading.Event()

        def delayed_prefetch(*_args, **_kwargs):
            started.set()
            release.wait(2)
            return {"item": next_item, "stream": "old-prefetch"}

        try:
            with mock.patch.object(flow, "fetch_play", side_effect=delayed_prefetch):
                flow._prefetch_one(session, next_item, options)
                self.assertTrue(started.wait(1))
                future = session["prep_jobs"][key]
                flow._cache_evict(key)
                flow._cache_set(key, {"item": next_item, "stream": "fresh-retry"})
                release.set()
                future.result(timeout=1)
                deadline = stdlib_time.monotonic() + 1
                while (
                    key in session["prep_jobs"] and stdlib_time.monotonic() < deadline
                ):
                    stdlib_time.sleep(0.01)
                self.assertNotIn(key, session["prep_jobs"])
                self.assertTrue(flow.try_next(context))
        finally:
            release.set()

        self.assertEqual(player.state.current_path, "fresh-retry")


if __name__ == "__main__":
    unittest.main()
