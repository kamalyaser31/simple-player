import concurrent.futures
import threading
import types
import unittest
from unittest import mock

from update import actions
from update.service import UpdateInfo


class Settings:
    def get_check_app_updates(self):
        return True

    def get_check_yt_updates_startup(self):
        return False


class UpdateRuntimeTests(unittest.TestCase):
    def test_update_completion_after_shutdown_does_not_reach_ui(self):
        started = threading.Event()
        release = threading.Event()
        scheduled = []
        context = types.SimpleNamespace(frame=object(), settings=Settings())

        def fetch_update_info():
            started.set()
            release.wait(2)
            return UpdateInfo(version="999.0", changes="test")

        previous_shutdown = actions._SHUTTING_DOWN
        previous_background = dict(actions._BG_FUTURES)
        previous_active = dict(actions._ACTIVE_TASKS)
        future = None
        try:
            actions._SHUTTING_DOWN = False
            with mock.patch.object(
                actions.service, "fetch_update_info", side_effect=fetch_update_info
            ), mock.patch.object(
                actions.wx,
                "CallAfter",
                side_effect=lambda *args: scheduled.append(args),
            ):
                actions.check_updates_on_startup(context)
                self.assertTrue(started.wait(1))
                future = next(iter(actions._BG_FUTURES))
                actions.shutdown_updates()
                release.set()
                self.assertIsNone(future.result(timeout=1))
                self.assertEqual(scheduled, [])
        finally:
            release.set()
            if future is not None and not future.done():
                concurrent.futures.wait([future], timeout=2)
            actions._BG_FUTURES.clear()
            actions._BG_FUTURES.update(previous_background)
            actions._ACTIVE_TASKS.clear()
            actions._ACTIVE_TASKS.update(previous_active)
            actions._SHUTTING_DOWN = previous_shutdown


if __name__ == "__main__":
    unittest.main()
