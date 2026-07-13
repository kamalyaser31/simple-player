import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_project_consistency.py"
SPEC = importlib.util.spec_from_file_location("project_consistency", SCRIPT)
CONSISTENCY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONSISTENCY)


class ConsistencyTests(unittest.TestCase):
    def test_current_project_is_consistent(self):
        self.assertEqual(CONSISTENCY.validate_project(SCRIPT.parents[1]), [])

    def test_version_check_reports_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            (repository / "info.json").write_text(
                json.dumps({"version": "1.0.0"}), encoding="utf-8"
            )
            errors = []
            CONSISTENCY._check_versions(
                repository,
                {"APP_VERSION": "2.0.0"},
                '#define MyAppVersion "1.0.0"',
                errors,
            )
        self.assertEqual(len(errors), 1)

    def test_extension_check_reports_every_duplicate_registry_drift(self):
        player = SCRIPT.parents[1]
        constants = CONSISTENCY._assignments(player / "config" / "constants.py")
        associations = CONSISTENCY._assignments(player / "config" / "file_associations.py")
        dialogs = CONSISTENCY._assignments(player / "ui" / "dialogs.py")
        installer = (player / "simple_audio_player.iss").read_text(encoding="utf-8")
        scenarios = [
            (
                "file dialog",
                {"AUDIO_WILDCARD": "*.mp3"},
                installer,
                "Audio extensions differ",
            )
        ]
        for name, pattern in CONSISTENCY._INSTALLER_EXTENSION_PATTERNS.items():
            drifted = CONSISTENCY.re.sub(pattern, "", installer, count=1)
            scenarios.append((name, dialogs, drifted, f"Inno {name}"))

        for name, dialog_values, installer_text, expected_error in scenarios:
            with self.subTest(registry=name):
                errors = []
                CONSISTENCY._check_associations(
                    constants,
                    associations,
                    dialog_values,
                    installer_text,
                    errors,
                )
                self.assertTrue(any(expected_error in error for error in errors))


if __name__ == "__main__":
    unittest.main()
