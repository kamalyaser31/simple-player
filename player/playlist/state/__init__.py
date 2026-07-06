import random

from .core import PlaylistStateCoreMixin
from .load import PlaylistStateLoadMixin
from .navigation import PlaylistStateNavigationMixin
from .mutations import PlaylistStateMutationsMixin
from .marks import PlaylistStateMarksMixin
from .meta import PlaylistStateMetaMixin


class PlaylistState(
    PlaylistStateCoreMixin,
    PlaylistStateLoadMixin,
    PlaylistStateNavigationMixin,
    PlaylistStateMutationsMixin,
    PlaylistStateMarksMixin,
    PlaylistStateMetaMixin,
):
    def __init__(self):
        self._file_list = []
        self._current_index = -1
        self._current_path = None
        self._pending_start = None
        self._meta = {}

        self._shuffle_enabled = False
        self._repeat_file_enabled = False
        self._shuffle_order = []
        self._shuffle_position = -1
        self._rng = random.Random()

        self._marked_keys = set()
