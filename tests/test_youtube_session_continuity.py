from tests.helpers.youtube_fakes import (
    FakeCancel,
    FakeCtx,
    FakeFuture,
    install_flow_import_stubs,
    yt_item,
)

install_flow_import_stubs()

from youtube import flow
from youtube.state import cleanup_ses, mk_ses, set_ses, sync_removed_sources


def _session(urls):
    ses = mk_ses("search", "Videos", [yt_item(url) for url in urls])
    ses.update({"audio_only": True, "quality": "medium"})
    return ses


def test_closing_secondary_results_session_keeps_active_playback_session():
    ctx = FakeCtx()
    active = _session(["https://youtu.be/a", "https://youtu.be/b"])
    secondary = _session(["https://youtu.be/x"])
    set_ses(ctx, active, 0)

    cleanup_ses(ctx, secondary)

    assert ctx.yt_pl is active


def test_targeted_cleanup_cancels_only_supplied_session_jobs():
    ctx = FakeCtx()
    active = _session(["https://youtu.be/a"])
    other = _session(["https://youtu.be/x"])
    active_future = FakeFuture(done=False)
    other_future = FakeFuture(done=False)
    active["prep_jobs"] = {"a": active_future}
    other["prep_jobs"] = {"x": other_future}
    other["cancel"] = FakeCancel()
    set_ses(ctx, active, 0)

    cleanup_ses(ctx, other)

    assert ctx.yt_pl is active
    assert not active_future.cancelled
    assert other_future.cancelled
    assert other["cancel"].is_set()


def test_removed_player_sources_clear_matching_queued_and_pending_state():
    ses = _session(["https://youtu.be/a", "https://youtu.be/b"])
    ses["queued"] = {"https://youtu.be/a", "https://youtu.be/b"}
    ses["pending_next"] = {"source": "https://youtu.be/b", "key": "https://youtu.be/b|a=1|q=medium"}

    sync_removed_sources(ses, ["https://youtu.be/b"])

    assert ses["queued"] == {"https://youtu.be/a"}
    assert ses["pending_next"] is None


def test_explicit_next_requeues_stale_session_item_after_return_to_results():
    ctx = FakeCtx()
    ses = _session(["https://youtu.be/a", "https://youtu.be/b"])
    ctx.player.current_source = "https://youtu.be/a"
    ctx.player.sources = ["https://youtu.be/a"]
    ses["queued"] = {"https://youtu.be/b"}
    set_ses(ctx, ses, 0)
    flow._cache_set(flow._prep_key("https://youtu.be/b", flow._opts(ctx, ses)), {"item": ses["items"][1], "stream": "stream-b"})

    assert flow.try_next(ctx) is True
    assert ctx.player.queued_streams == [("stream-b", "https://youtu.be/b", "https://youtu.be/b")]
    assert ctx.player.next_calls == 1


def test_natural_end_uses_active_youtube_session_next_handling():
    ctx = FakeCtx()
    ses = _session(["https://youtu.be/a", "https://youtu.be/b"])
    ctx.player.current_source = "https://youtu.be/a"
    ctx.player.sources = ["https://youtu.be/a"]
    set_ses(ctx, ses, 0)
    flow._cache_set(flow._prep_key("https://youtu.be/b", flow._opts(ctx, ses)), {"item": ses["items"][1], "stream": "stream-b"})

    assert flow.on_playback_finished(ctx) is True
    assert ctx.player.next_calls == 1


def test_unavailable_next_item_gives_feedback_without_clearing_state(monkeypatch):
    ctx = FakeCtx()
    ses = _session(["https://youtu.be/a", "https://youtu.be/b"])
    ctx.player.current_source = "https://youtu.be/a"
    ctx.player.sources = ["https://youtu.be/a"]
    set_ses(ctx, ses, 0)

    monkeypatch.setattr(flow, "_load_next_bg", lambda _ctx, _ses, _item, _from, _to: None)

    assert flow.on_playback_finished(ctx) is True
    assert ctx.yt_pl is ses
    assert ctx.player.current_source == "https://youtu.be/a"


def test_non_youtube_eof_keeps_existing_local_advance_behavior():
    from core.player.lifecycle import PlayerLifecycleMixin

    class State:
        current_path = "local.mp3"

        def __init__(self):
            self.next_calls = 0

        def is_repeat_file_enabled(self):
            return False

        def next_track(self, use_shuffle=True, wrap=False):
            self.next_calls += 1
            return True

    class Player(PlayerLifecycleMixin):
        def __init__(self):
            self._state = State()
            self._end_behavior = "advance"
            self._wrap_playlist_enabled = False
            self.loaded = 0
            self.stopped = 0
            self._finished_file_handler = lambda: False

        def _load_current(self):
            self.loaded += 1

        def stop(self):
            self.stopped += 1

    player = Player()

    player._handle_finished_file()

    assert player._state.next_calls == 1
    assert player.loaded == 1
    assert player.stopped == 0
