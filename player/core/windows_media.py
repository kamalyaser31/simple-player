import ctypes
import os
from datetime import timedelta

from actions import (
    NEXT_TRACK,
    PLAY_PAUSE,
    PREVIOUS_TRACK,
    SEEK_BACKWARD,
    SEEK_FORWARD,
)

try:
    from winsdk.windows.media import (
        MediaPlaybackStatus,
        MediaPlaybackType,
        SystemMediaTransportControlsButton,
        SystemMediaTransportControlsTimelineProperties,
    )
    from winsdk.windows.media.playback import MediaPlayer

    _WINSDK_OK = True
except Exception:
    _WINSDK_OK = False


class WindowsMediaBridge:
    def __init__(self, app_id, app_name, on_action=None):
        self._app_name = str(app_name or "").strip() or "Simple Audio Player"
        self._on_action = on_action
        self._player = None
        self._smtc = None
        self._button_token = None
        self._enabled = False
        self._last_title = ""
        self._last_artist = ""

        if os.name != "nt":
            return
        _set_app_id(app_id)
        if not _WINSDK_OK:
            return
        self._init_session()

    @property
    def is_enabled(self):
        return bool(self._enabled)

    def close(self):
        smtc = self._smtc
        self._smtc = None
        token = self._button_token
        self._button_token = None
        if smtc is not None and token is not None:
            try:
                smtc.remove_button_pressed(token)
            except Exception:
                pass

        player = self._player
        self._player = None
        if player is not None:
            try:
                player.close()
            except Exception:
                pass
        self._enabled = False

    def update(
        self,
        *,
        has_media,
        is_playing,
        title="",
        artist="",
        duration=None,
        position=None,
        can_next=False,
        can_previous=False,
    ):
        if not self._enabled or self._smtc is None:
            return

        smtc = self._smtc
        has_media = bool(has_media)
        is_playing = bool(is_playing) if has_media else False

        smtc.is_play_enabled = has_media
        smtc.is_pause_enabled = has_media
        smtc.is_next_enabled = has_media and bool(can_next)
        smtc.is_previous_enabled = has_media and bool(can_previous)
        smtc.is_fast_forward_enabled = has_media
        smtc.is_rewind_enabled = has_media
        smtc.is_stop_enabled = has_media

        if not has_media:
            smtc.playback_status = MediaPlaybackStatus.CLOSED
            self._clear_display()
            return

        smtc.playback_status = (
            MediaPlaybackStatus.PLAYING if is_playing else MediaPlaybackStatus.PAUSED
        )
        self._update_display(title=title, artist=artist)
        self._update_timeline(duration=duration, position=position)

    def _init_session(self):
        try:
            player = MediaPlayer()
        except Exception:
            return

        self._player = player
        try:
            self._player.command_manager.is_enabled = False
        except Exception:
            pass

        try:
            smtc = self._player.system_media_transport_controls
        except Exception:
            self.close()
            return

        self._smtc = smtc
        try:
            smtc.is_enabled = True
        except Exception:
            self.close()
            return

        smtc.is_play_enabled = True
        smtc.is_pause_enabled = True
        smtc.is_next_enabled = True
        smtc.is_previous_enabled = True
        smtc.is_fast_forward_enabled = True
        smtc.is_rewind_enabled = True
        smtc.is_stop_enabled = True

        if callable(self._on_action):
            try:
                self._button_token = smtc.add_button_pressed(self._on_button_pressed)
            except Exception:
                self._button_token = None

        self._enabled = True

    def _on_button_pressed(self, _sender, args):
        action_id = None
        try:
            button = args.button
            if button in (
                SystemMediaTransportControlsButton.PLAY,
                SystemMediaTransportControlsButton.PAUSE,
            ):
                action_id = PLAY_PAUSE
            elif button == SystemMediaTransportControlsButton.NEXT:
                action_id = NEXT_TRACK
            elif button == SystemMediaTransportControlsButton.PREVIOUS:
                action_id = PREVIOUS_TRACK
            elif button == SystemMediaTransportControlsButton.FAST_FORWARD:
                action_id = SEEK_FORWARD
            elif button == SystemMediaTransportControlsButton.REWIND:
                action_id = SEEK_BACKWARD
        except Exception:
            action_id = None

        if action_id and callable(self._on_action):
            try:
                self._on_action(action_id)
            except Exception:
                pass

    def _update_display(self, *, title, artist):
        if self._smtc is None:
            return
        title_text = str(title or "").strip() or self._app_name
        artist_text = str(artist or "").strip() or self._app_name
        if title_text == self._last_title and artist_text == self._last_artist:
            return
        self._last_title = title_text
        self._last_artist = artist_text
        try:
            updater = self._smtc.display_updater
            updater.type = MediaPlaybackType.MUSIC
            props = updater.music_properties
            props.title = title_text
            props.artist = artist_text
            updater.update()
        except Exception:
            pass

    def _clear_display(self):
        if self._smtc is None:
            return
        if not self._last_title and not self._last_artist:
            return
        self._last_title = ""
        self._last_artist = ""
        try:
            updater = self._smtc.display_updater
            updater.type = MediaPlaybackType.UNKNOWN
            props = updater.music_properties
            props.title = ""
            props.artist = ""
            updater.update()
        except Exception:
            pass

    def _update_timeline(self, *, duration, position):
        if self._smtc is None:
            return
        duration_val = _safe_seconds(duration)
        position_val = _safe_seconds(position)
        if duration_val is None or duration_val <= 0:
            return
        if position_val is None:
            position_val = 0.0
        position_val = max(0.0, min(duration_val, position_val))
        try:
            timeline = SystemMediaTransportControlsTimelineProperties()
            start = timedelta(seconds=0)
            pos = timedelta(seconds=position_val)
            end = timedelta(seconds=duration_val)
            timeline.start_time = start
            timeline.min_seek_time = start
            timeline.position = pos
            timeline.max_seek_time = end
            timeline.end_time = end
            self._smtc.update_timeline_properties(timeline)
        except Exception:
            pass


def _safe_seconds(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number < 0:
        return 0.0
    return number


def _set_app_id(app_id):
    if os.name != "nt":
        return
    value = str(app_id or "").strip()
    if not value:
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(value)
    except Exception:
        pass
