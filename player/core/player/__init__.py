from core.player.files import PlayerFilesMixin
from core.player.filters import PlayerFiltersMixin
from core.player.lifecycle import PlayerLifecycleMixin
from core.player.load import PlayerLoadMixin
from core.player.playback import PlayerPlaybackMixin
from core.player.state import PlayerStateMixin
from core.player.window import PlayerWindowMixin
from playlist.state import PlaylistState


class Player(
    PlayerWindowMixin,
    PlayerLoadMixin,
    PlayerPlaybackMixin,
    PlayerFiltersMixin,
    PlayerStateMixin,
    PlayerFilesMixin,
    PlayerLifecycleMixin,
):
    def __init__(self):
        from core.mpv_engine import MpvEngine

        self._engine = MpvEngine(on_end_file=self._on_end_file_event)
        self._state = PlaylistState()
        self._end_behavior = "advance"
        self._wrap_playlist_enabled = False
        self._render_window_id = None
        self._audio_normalize_enabled = False
        self._audio_mono_enabled = False
        self._silence_removal_enabled = False
        self._silence_removal_options = {}

