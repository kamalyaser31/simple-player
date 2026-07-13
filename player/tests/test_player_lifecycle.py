import unittest

from core.player.lifecycle import END_FILE_REASON_ERROR, PlayerLifecycleMixin


class State:
    current_path = "stream"

    def is_repeat_file_enabled(self):
        return False


class Player(PlayerLifecycleMixin):
    def __init__(self):
        self._state = State()
        self._end_behavior = "advance"
        self._wrap_playlist_enabled = False
        self.reasons = []
        self._finished_file_handler = self._finished

    def _finished(self, reason):
        self.reasons.append(reason)
        return True


class PlayerLifecycleTests(unittest.TestCase):
    def test_playback_error_reason_reaches_finished_handler(self):
        player = Player()

        player._on_end_file_event({"event": {"reason": END_FILE_REASON_ERROR}})

        self.assertEqual(player.reasons, [END_FILE_REASON_ERROR])


if __name__ == "__main__":
    unittest.main()
