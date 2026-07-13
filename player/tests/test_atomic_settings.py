import configparser
import os
import tempfile
import unittest
from unittest import mock

from config.settings_manager import SettingsManager


class AtomicSettingsTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.directory.name, "settings.ini")
        self.settings = SettingsManager()
        self.settings._config_path = self.path
        self.settings.load()

    def tearDown(self):
        self.directory.cleanup()

    def test_save_writes_parseable_ini(self):
        self.settings.set_volume(321)
        self.settings.save(force=True)

        parsed = configparser.ConfigParser(interpolation=None)
        parsed.read(self.path, encoding="utf-8")
        self.assertEqual(parsed.getint("audio", "volume"), 321)

    def test_validation_failure_preserves_previous_file(self):
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write("[ui]\nsave_on_close = true\n")
        with mock.patch.object(
            self.settings,
            "_validate_temporary_config",
            side_effect=configparser.Error("invalid"),
        ):
            with self.assertRaises(configparser.Error):
                self.settings.save(force=True)

        with open(self.path, "r", encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "[ui]\nsave_on_close = true\n")
        self.assertFalse(any(name.endswith(".tmp") for name in os.listdir(self.directory.name)))

    def test_disabled_save_on_close_only_persists_that_flag(self):
        self.settings.set_volume(111)
        self.settings.save(force=True)
        self.settings.set_volume(999)
        self.settings.set_save_on_close(False)
        self.settings.save()

        parsed = configparser.ConfigParser(interpolation=None)
        parsed.read(self.path, encoding="utf-8")
        self.assertEqual(parsed.getint("audio", "volume"), 111)
        self.assertFalse(parsed.getboolean("ui", "save_on_close"))


if __name__ == "__main__":
    unittest.main()
