import tempfile
import types
import unittest
from unittest import mock

import wx

from config.settings_manager import SettingsManager
from core import controller


class ControllerRuntimeTests(unittest.TestCase):
    def test_shutdown_continues_after_subsystem_failures(self):
        calls = []
        app = controller.AppController.__new__(controller.AppController)
        app._ctx = object()
        app._global_keyboard = ShutdownAction(calls, "keyboard", fail=True)
        app._media_timer = Timer(calls)
        app._rec = Recorder(calls)
        app._settings = ShutdownSettings(calls)
        app._player = ShutdownPlayer(calls)
        app._media = ShutdownAction(calls, "media", method="close", fail=True)

        with mock.patch.object(
            controller, "shutdown_youtube", side_effect=RuntimeError("youtube")
        ), mock.patch.object(
            controller, "shutdown_updates", side_effect=lambda: calls.append("updates")
        ), mock.patch(
            "playlist.info.shutdown_info_jobs",
            side_effect=lambda: calls.append("playlist info"),
        ), mock.patch.object(controller._LOG, "exception"):
            app.shutdown()

        for expected in (
            "updates",
            "playlist info",
            "keyboard",
            "timer",
            "recorder",
            "volume",
            "speed",
            "settings save",
            "media",
            "player",
        ):
            self.assertIn(expected, calls)

    def test_settings_save_failure_restores_previous_runtime_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = SettingsManager()
            settings._config_path = f"{directory}\\settings.ini"
            settings.load()
            app = controller.AppController.__new__(controller.AppController)
            app._settings = settings
            app._ctx = types.SimpleNamespace(frame=object())
            dialog = SettingsDialog(settings)

            with mock.patch.object(
                controller, "SettingsDialog", return_value=dialog
            ), mock.patch.object(
                settings, "save", side_effect=OSError("disk full")
            ), mock.patch.object(controller.wx, "MessageBox") as message_box:
                app.open_settings_dialog()

        self.assertEqual(settings.get_volume(), 100)
        self.assertTrue(dialog.destroyed)
        message_box.assert_called_once()


class ShutdownAction:
    def __init__(self, calls, name, method="stop", fail=False):
        self.calls = calls
        self.name = name
        self.fail = fail
        setattr(self, method, self.run)

    def run(self, *args, **kwargs):
        self.calls.append(self.name)
        if self.fail:
            raise RuntimeError(self.name)


class Timer:
    def __init__(self, calls):
        self.calls = calls

    def IsRunning(self):
        return True

    def Stop(self):
        self.calls.append("timer")


class Recorder:
    def __init__(self, calls):
        self.calls = calls

    def stop(self, beep=False):
        self.calls.append("recorder")


class ShutdownSettings:
    def __init__(self, calls):
        self.calls = calls

    def get_save_file_pos(self):
        return False

    def set_volume(self, value):
        self.calls.append("volume")

    def set_speed(self, value):
        self.calls.append("speed")

    def get_remember_position(self):
        return False

    def save(self):
        self.calls.append("settings save")
        raise OSError("disk full")


class ShutdownPlayer:
    current_path = None

    def __init__(self, calls):
        self.calls = calls

    def get_volume(self):
        return 100

    def get_speed(self):
        return 1.0

    def shutdown(self):
        self.calls.append("player")


class SettingsDialog:
    def __init__(self, settings):
        self.settings = settings
        self.destroyed = False

    def ShowModal(self):
        return wx.ID_OK

    def apply(self):
        self.settings.set_volume(700)

    def Destroy(self):
        self.destroyed = True


if __name__ == "__main__":
    unittest.main()
