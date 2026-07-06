import os
import sys
import types


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
PLAYER_ROOT = os.path.join(ROOT, "player")
if PLAYER_ROOT not in sys.path:
    sys.path.insert(0, PLAYER_ROOT)


def install_wx_stub():
    wx = types.SimpleNamespace(
        ID_OK=1,
        ID_CANCEL=2,
        OK=0,
        ICON_ERROR=0,
        CallAfter=lambda func, *args, **kwargs: func(*args, **kwargs),
        MessageBox=lambda *args, **kwargs: None,
    )
    sys.modules.setdefault("wx", wx)
    return wx


def install_flow_import_stubs():
    install_wx_stub()
    sys.modules.setdefault(
        "ui.yt_dialogs",
        types.SimpleNamespace(ResultsDlg=object, MissingDlg=object),
    )
    sys.modules.setdefault(
        "ui.task_dialogs",
        types.SimpleNamespace(TaskDlg=object, BusyDlg=object),
    )
    sys.modules.setdefault(
        "youtube.video",
        types.SimpleNamespace(
            dl_url=lambda *_args, **_kwargs: None,
            copy_link=lambda *_args, **_kwargs: None,
            dl_now=lambda *_args, **_kwargs: None,
            has_video=lambda *_args, **_kwargs: False,
            show_desc=lambda *_args, **_kwargs: None,
        ),
    )


class FakeFuture:
    def __init__(self, done=False):
        self._done = bool(done)
        self.cancelled = False

    def done(self):
        return self._done

    def cancel(self):
        self.cancelled = True
        self._done = True


class FakeCancel:
    def __init__(self):
        self.cancelled = False

    def set(self):
        self.cancelled = True

    def is_set(self):
        return self.cancelled


class FakeSettings:
    def get_yt_prefetch_count(self):
        return 0

    def get_yt_audio_only(self):
        return True

    def get_yt_video_quality(self):
        return "medium"


class FakePlayer:
    def __init__(self):
        self.current_source = ""
        self.current_path = ""
        self.sources = []
        self.queued_streams = []
        self.next_calls = 0
        self.removed_sources = []

    def has_source(self, source):
        return str(source or "") in self.sources

    def queue_stream(self, stream, title=None, source_url=None):
        self.queued_streams.append((stream, title, source_url))
        self.sources.append(str(source_url or ""))
        return True

    def next_track(self):
        self.next_calls += 1
        return True

    def remove_sources(self, sources):
        source_set = {str(value or "") for value in sources or []}
        self.removed_sources.extend(source_set)
        self.sources = [source for source in self.sources if source not in source_set]
        return True

    def stop(self):
        pass


class FakeCtx:
    def __init__(self):
        self.player = FakePlayer()
        self.settings = FakeSettings()
        self.frame = object()
        self.yt_pl = None
        self.yt_now = None
        self.spoken = []

    def speak(self, text, fallback=None):
        self.spoken.append((text, fallback))

    def reset_selection(self):
        pass

    def set_file_loaded(self, _value):
        pass

    def set_playing(self, _value):
        pass


def yt_item(url, title=None):
    install_flow_import_stubs()
    from youtube.resolver import YtItem

    return YtItem(
        title=title or url,
        url=url,
        channel_url="",
        channel_name="",
        description="",
    )
