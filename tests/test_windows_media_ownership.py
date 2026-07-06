import importlib
import sys
import types

from tests.helpers.youtube_fakes import install_flow_import_stubs

install_flow_import_stubs()


def test_mpv_windows_media_controls_are_disabled_for_custom_bridge(monkeypatch):
    class FakeMPV:
        def __init__(self, **_options):
            self.values = {}

        def __setitem__(self, key, value):
            self.values[key] = value

        def event_callback(self, _name):
            return lambda func: func

    monkeypatch.setitem(sys.modules, "mpv", types.SimpleNamespace(MPV=FakeMPV))
    from core import mpv_engine

    monkeypatch.setattr(mpv_engine.os, "name", "nt")
    engine = mpv_engine.MpvEngine()

    assert engine._mpv.values[mpv_engine.MEDIA_CONTROLS_OPTION] == "no"
    assert engine._mpv.values[mpv_engine.MEDIA_KEYS_OPTION] == "no"


def test_windows_media_bridge_unavailable_fallback_is_safe(monkeypatch):
    from core import windows_media

    monkeypatch.setattr(windows_media.os, "name", "nt")
    monkeypatch.setattr(windows_media, "_WINSDK_OK", False)
    monkeypatch.setattr(windows_media, "_set_app_id", lambda _app_id: None)

    bridge = windows_media.WindowsMediaBridge("app", "App")
    bridge.update(has_media=True, is_playing=True, title="Title")
    bridge.close()

    assert not bridge.is_enabled


def test_media_bridge_routes_one_action_per_button_callback(monkeypatch):
    from core import windows_media

    buttons = types.SimpleNamespace(
        PLAY="play",
        PAUSE="pause",
        NEXT="next",
        PREVIOUS="previous",
        FAST_FORWARD="fast_forward",
        REWIND="rewind",
    )
    monkeypatch.setattr(windows_media, "SystemMediaTransportControlsButton", buttons, raising=False)
    actions = []
    bridge = windows_media.WindowsMediaBridge("app", "App", on_action=actions.append)
    bridge._on_action = actions.append
    button = types.SimpleNamespace(button=buttons.NEXT)

    bridge._on_button_pressed(None, button)

    assert actions == [windows_media.NEXT_TRACK]
