import configparser
import os

from config.constants import (
    APP_NAME,
    CONFIG_FILENAME,
    SPEED_STEP,
    VOLUME_MAX,
    VOLUME_MIN,
    VOLUME_STEP,
    YT_DLP_DEFAULT_CHANNEL,
    YT_DLP_UPDATE_CHANNELS,
)
from config.shortcut_utils import shortcut_from_config, shortcut_to_config
from helpers.utils import clamp


SILENCE_REMOVAL_OPTION_KEYS = (
    "start_periods",
    "start_duration",
    "threshold",
    "stop_periods",
    "stop_duration",
    "stop_silence",
    "window",
    "detection",
)

SILENCE_REMOVAL_DEFAULTS = {
    "start_periods": "1",
    "start_duration": "0.2",
    "threshold": "-30",
    "stop_periods": "-1",
    "stop_duration": "0.5",
    "stop_silence": "0.2",
    "window": "0.02",
    "detection": "peak",
}

SILENCE_REMOVAL_DETECTION_MODES = ("peak", "rms")
SILENCE_REMOVAL_SECTION = "silence_removal"

LEGACY_AUDIO_SILENCE_KEYS = (
    "silence_removal_enabled",
    "silence_start_periods",
    "silence_start_duration",
    "silence_threshold",
    "silence_stop_periods",
    "silence_stop_duration",
    "silence_stop_silence",
    "silence_window",
    "silence_detection",
    "silence_silence_threshold",
    "silence_start_threshold",
    "silence_stop_threshold",
)


def _default_rec_folder():
    docs = ""
    if os.name == "nt":
        docs = os.path.join(os.path.expanduser("~"), "Documents")
    if not docs:
        docs = os.path.join(os.path.expanduser("~"), "Documents")
    return os.path.join(docs, APP_NAME, "recordings")


class SettingsManager:
    def __init__(self):
        self._config = configparser.ConfigParser(interpolation=None)
        self._config_path = self._resolve_config_path()
        self._defaults = {
            "audio": {
                "volume": "100",
                "speed": "1.0",
                "device": "",
                "seek_step_key": "2",
                "seek_step_custom": "5",
                "speed_step": str(float(SPEED_STEP)),
                "volume_step": str(int(VOLUME_STEP)),
                "end_behavior": "advance",
                "wrap_playlist": "false",
                "save_file_pos": "false",
                "audio_normalize_enabled": "true",
                "audio_mono_enabled": "false",
            },
            SILENCE_REMOVAL_SECTION: {
                "enabled": "false",
                "advanced": "false",
                "start_periods": SILENCE_REMOVAL_DEFAULTS["start_periods"],
                "start_duration": SILENCE_REMOVAL_DEFAULTS["start_duration"],
                "threshold": SILENCE_REMOVAL_DEFAULTS["threshold"],
                "stop_periods": SILENCE_REMOVAL_DEFAULTS["stop_periods"],
                "stop_duration": SILENCE_REMOVAL_DEFAULTS["stop_duration"],
                "stop_silence": SILENCE_REMOVAL_DEFAULTS["stop_silence"],
                "window": SILENCE_REMOVAL_DEFAULTS["window"],
                "detection": SILENCE_REMOVAL_DEFAULTS["detection"],
            },
            "ui": {
                "last_dir": "",
                "verbosity": "beginner",
                "open_with_files_mode": "file_only",
                "check_app_updates": "true",
                "save_on_close": "true",
                "speak_file_on_nav": "false",
                "language": "system",
            },
            "youtube": {
                "skip_prompt": "false",
                "audio_only": "true",
                "video_quality": "medium",
                "mixed_link_mode": "ask",
                "yt_dlp_channel": YT_DLP_DEFAULT_CHANNEL,
            },
            "recording": {
                "channels": "stereo",
                "quality": "192",
                "format": "wav",
                "folder": _default_rec_folder(),
            },
            "playback": {
                "remember_position": "false",
                "last_file": "",
                "last_position": "0",
            },
        }

    def _resolve_config_path(self):
        if os.name == "nt":
            base_dir = os.environ.get("APPDATA", "")
            if not base_dir:
                home = os.path.expanduser("~")
                base_dir = os.path.join(home, "AppData", "Roaming")
        else:
            base_dir = os.environ.get("XDG_CONFIG_HOME", "")
            if not base_dir:
                base_dir = os.path.join(os.path.expanduser("~"), ".config")
        app_dir = os.path.join(base_dir, APP_NAME)
        os.makedirs(app_dir, exist_ok=True)
        return os.path.join(app_dir, CONFIG_FILENAME)

    @property
    def config_path(self):
        return self._config_path

    def load(self):
        self._config.read_dict(self._defaults)
        has_new_silence_section = False
        if os.path.exists(self._config_path):
            try:
                self._config.read(self._config_path, encoding="utf-8")
                raw_config = configparser.ConfigParser(interpolation=None)
                raw_config.read(self._config_path, encoding="utf-8")
                has_new_silence_section = raw_config.has_section(SILENCE_REMOVAL_SECTION)
            except (configparser.Error, OSError):
                # Fall back to defaults if settings file is corrupted.
                self._config = configparser.ConfigParser(interpolation=None)
                self._config.read_dict(self._defaults)
                has_new_silence_section = False
        self._migrate_silence_removal_settings(has_new_silence_section)

    def save(self):
        if self.get_save_on_close():
            self._write_config(self._config)
            return
        self._save_save_on_close_only()

    def _save_save_on_close_only(self):
        disk = configparser.ConfigParser(interpolation=None)
        if os.path.exists(self._config_path):
            try:
                disk.read(self._config_path, encoding="utf-8")
            except (configparser.Error, OSError):
                disk = configparser.ConfigParser(interpolation=None)
        if not disk.sections():
            disk.read_dict(self._defaults)
        if "ui" not in disk:
            disk["ui"] = {}
        disk["ui"]["save_on_close"] = "false"
        self._write_config(disk)

    def _write_config(self, parser):
        with open(self._config_path, "w", encoding="utf-8") as handle:
            parser.write(handle)

    def reset_to_defaults(self):
        self._config = configparser.ConfigParser(interpolation=None)
        self._config.read_dict(self._defaults)
        self._migrate_silence_removal_settings(has_new_silence_section=True)
        self.save()

    def get_volume(self):
        try:
            volume = int(self._config.get("audio", "volume"))
        except (ValueError, configparser.Error):
            volume = 100
        return clamp(volume, VOLUME_MIN, VOLUME_MAX)

    def set_volume(self, volume):
        if "audio" not in self._config:
            self._config["audio"] = {}
        self._config["audio"]["volume"] = str(int(volume))

    def get_last_dir(self):
        return self._config.get("ui", "last_dir", fallback="")

    def set_last_dir(self, path):
        if "ui" not in self._config:
            self._config["ui"] = {}
        self._config["ui"]["last_dir"] = path or ""

    def get_verbosity(self):
        return self._config.get("ui", "verbosity", fallback="beginner").lower()

    def set_verbosity(self, value):
        if "ui" not in self._config:
            self._config["ui"] = {}
        self._config["ui"]["verbosity"] = value or "beginner"

    def get_open_with_files_mode(self):
        value = self._config.get("ui", "open_with_files_mode", fallback="file_only")
        value = (value or "file_only").lower()
        if value not in ("file_only", "main_folder", "main_and_subfolders"):
            return "file_only"
        return value

    def set_open_with_files_mode(self, value):
        if "ui" not in self._config:
            self._config["ui"] = {}
        value = (value or "file_only").lower()
        if value not in ("file_only", "main_folder", "main_and_subfolders"):
            value = "file_only"
        self._config["ui"]["open_with_files_mode"] = value

    def get_check_app_updates(self):
        try:
            return self._config.getboolean("ui", "check_app_updates")
        except (ValueError, configparser.Error):
            return True

    def set_check_app_updates(self, enabled):
        if "ui" not in self._config:
            self._config["ui"] = {}
        self._config["ui"]["check_app_updates"] = "true" if enabled else "false"

    def get_save_on_close(self):
        try:
            return self._config.getboolean("ui", "save_on_close")
        except (ValueError, configparser.Error):
            return True

    def set_save_on_close(self, enabled):
        if "ui" not in self._config:
            self._config["ui"] = {}
        self._config["ui"]["save_on_close"] = "true" if enabled else "false"

    def get_speak_file_on_nav(self):
        try:
            return self._config.getboolean("ui", "speak_file_on_nav")
        except (ValueError, configparser.Error):
            return False

    def set_speak_file_on_nav(self, enabled):
        if "ui" not in self._config:
            self._config["ui"] = {}
        self._config["ui"]["speak_file_on_nav"] = "true" if enabled else "false"

    def get_ui_language(self):
        text = self._config.get("ui", "language", fallback="system")
        text = str(text or "system").strip()
        return text or "system"

    def set_ui_language(self, language_code):
        if "ui" not in self._config:
            self._config["ui"] = {}
        text = str(language_code or "system").strip()
        self._config["ui"]["language"] = text or "system"

    def get_yt_skip_prompt(self):
        try:
            return self._config.getboolean("youtube", "skip_prompt")
        except (ValueError, configparser.Error):
            return False

    def set_yt_skip_prompt(self, value):
        if "youtube" not in self._config:
            self._config["youtube"] = {}
        self._config["youtube"]["skip_prompt"] = "true" if value else "false"

    def get_yt_audio_only(self):
        try:
            return self._config.getboolean("youtube", "audio_only")
        except (ValueError, configparser.Error):
            return True

    def set_yt_audio_only(self, enabled):
        if "youtube" not in self._config:
            self._config["youtube"] = {}
        self._config["youtube"]["audio_only"] = "true" if enabled else "false"

    def get_yt_video_quality(self):
        value = self._config.get("youtube", "video_quality", fallback="medium").lower()
        if value not in ("low", "medium", "best"):
            return "medium"
        return value

    def set_yt_video_quality(self, value):
        if "youtube" not in self._config:
            self._config["youtube"] = {}
        text = str(value or "medium").strip().lower()
        if text not in ("low", "medium", "best"):
            text = "medium"
        self._config["youtube"]["video_quality"] = text

    def get_yt_mixed_link_mode(self):
        value = self._config.get("youtube", "mixed_link_mode", fallback="ask")
        value = str(value or "ask").strip().lower()
        if value not in ("ask", "video", "playlist"):
            return "ask"
        return value

    def set_yt_mixed_link_mode(self, value):
        if "youtube" not in self._config:
            self._config["youtube"] = {}
        text = str(value or "ask").strip().lower()
        if text not in ("ask", "video", "playlist"):
            text = "ask"
        self._config["youtube"]["mixed_link_mode"] = text

    def get_yt_dlp_channel(self):
        value = self._config.get(
            "youtube",
            "yt_dlp_channel",
            fallback=YT_DLP_DEFAULT_CHANNEL,
        ).lower()
        if value not in YT_DLP_UPDATE_CHANNELS:
            return YT_DLP_DEFAULT_CHANNEL
        return value

    def set_yt_dlp_channel(self, channel):
        if "youtube" not in self._config:
            self._config["youtube"] = {}
        value = str(channel or YT_DLP_DEFAULT_CHANNEL).strip().lower()
        if value not in YT_DLP_UPDATE_CHANNELS:
            value = YT_DLP_DEFAULT_CHANNEL
        self._config["youtube"]["yt_dlp_channel"] = value

    def get_rec_channels(self):
        value = str(
            self._config.get("recording", "channels", fallback="stereo") or "stereo"
        ).strip().lower()
        if value not in ("mono", "stereo"):
            return "stereo"
        return value

    def set_rec_channels(self, value):
        if "recording" not in self._config:
            self._config["recording"] = {}
        text = str(value or "stereo").strip().lower()
        if text not in ("mono", "stereo"):
            text = "stereo"
        self._config["recording"]["channels"] = text

    def get_rec_quality(self):
        try:
            val = int(self._config.get("recording", "quality", fallback="192"))
        except (ValueError, configparser.Error):
            val = 192
        return int(clamp(val, 32, 320))

    def set_rec_quality(self, value):
        if "recording" not in self._config:
            self._config["recording"] = {}
        try:
            val = int(value)
        except (TypeError, ValueError):
            val = 192
        self._config["recording"]["quality"] = str(int(clamp(val, 32, 320)))

    def get_rec_format(self):
        value = str(
            self._config.get("recording", "format", fallback="wav") or "wav"
        ).strip().lower()
        if value not in ("wav", "mp3"):
            return "wav"
        return value

    def set_rec_format(self, value):
        if "recording" not in self._config:
            self._config["recording"] = {}
        text = str(value or "wav").strip().lower()
        if text not in ("wav", "mp3"):
            text = "wav"
        self._config["recording"]["format"] = text

    def get_rec_folder(self):
        value = str(
            self._config.get("recording", "folder", fallback=_default_rec_folder())
            or ""
        ).strip()
        if not value:
            return _default_rec_folder()
        return value

    def set_rec_folder(self, value):
        if "recording" not in self._config:
            self._config["recording"] = {}
        text = str(value or "").strip()
        self._config["recording"]["folder"] = text or _default_rec_folder()

    def get_remember_position(self):
        try:
            return self._config.getboolean("playback", "remember_position")
        except (ValueError, configparser.Error):
            return False

    def set_remember_position(self, enabled):
        if "playback" not in self._config:
            self._config["playback"] = {}
        self._config["playback"]["remember_position"] = "true" if enabled else "false"

    def get_last_file(self):
        return self._config.get("playback", "last_file", fallback="")

    def get_last_position(self):
        try:
            return float(self._config.get("playback", "last_position"))
        except (ValueError, configparser.Error):
            return 0.0

    def get_speed(self):
        try:
            return float(self._config.get("audio", "speed"))
        except (ValueError, configparser.Error):
            try:
                return float(self._config.get("playback", "speed"))
            except (ValueError, configparser.Error):
                return 1.0

    def set_last_file_position(self, path, position):
        if "playback" not in self._config:
            self._config["playback"] = {}
        self._config["playback"]["last_file"] = path or ""
        self._config["playback"]["last_position"] = str(float(position or 0.0))

    def set_speed(self, speed):
        if "audio" not in self._config:
            self._config["audio"] = {}
        self._config["audio"]["speed"] = str(float(speed or 1.0))

    def get_audio_device(self):
        return self._config.get("audio", "device", fallback="")

    def set_audio_device(self, device_name):
        if "audio" not in self._config:
            self._config["audio"] = {}
        self._config["audio"]["device"] = device_name or ""

    def get_seek_step_key(self):
        return self._config.get("audio", "seek_step_key", fallback="2")

    def set_seek_step_key(self, key):
        if "audio" not in self._config:
            self._config["audio"] = {}
        self._config["audio"]["seek_step_key"] = key or "2"

    def get_seek_step_custom(self):
        try:
            return float(self._config.get("audio", "seek_step_custom"))
        except (ValueError, configparser.Error):
            return 5.0

    def set_seek_step_custom(self, value):
        if "audio" not in self._config:
            self._config["audio"] = {}
        self._config["audio"]["seek_step_custom"] = str(float(value))

    def get_speed_step(self):
        try:
            value = float(self._config.get("audio", "speed_step"))
        except (ValueError, configparser.Error):
            value = float(SPEED_STEP)
        if value <= 0:
            return float(SPEED_STEP)
        return float(value)

    def set_speed_step(self, value):
        if "audio" not in self._config:
            self._config["audio"] = {}
        try:
            step = float(value)
        except (ValueError, TypeError):
            step = float(SPEED_STEP)
        if step <= 0:
            step = float(SPEED_STEP)
        self._config["audio"]["speed_step"] = str(step)

    def get_volume_step(self):
        try:
            value = int(self._config.get("audio", "volume_step"))
        except (ValueError, configparser.Error):
            value = int(VOLUME_STEP)
        return int(clamp(value, 1, 20))

    def set_volume_step(self, value):
        if "audio" not in self._config:
            self._config["audio"] = {}
        try:
            step = int(value)
        except (ValueError, TypeError):
            step = int(VOLUME_STEP)
        step = int(clamp(step, 1, 20))
        self._config["audio"]["volume_step"] = str(step)

    def get_end_behavior(self):
        value = self._config.get("audio", "end_behavior", fallback="advance").lower()
        if value not in ("advance", "loop", "none"):
            return "advance"
        return value

    def set_end_behavior(self, value):
        if "audio" not in self._config:
            self._config["audio"] = {}
        value = (value or "advance").lower()
        if value not in ("advance", "loop", "none"):
            value = "advance"
        self._config["audio"]["end_behavior"] = value

    def get_wrap_playlist(self):
        try:
            return self._config.getboolean("audio", "wrap_playlist")
        except (ValueError, configparser.Error):
            return False

    def set_wrap_playlist(self, enabled):
        if "audio" not in self._config:
            self._config["audio"] = {}
        self._config["audio"]["wrap_playlist"] = "true" if enabled else "false"

    def get_save_file_pos(self):
        try:
            return self._config.getboolean("audio", "save_file_pos")
        except (ValueError, configparser.Error):
            return False

    def set_save_file_pos(self, enabled):
        if "audio" not in self._config:
            self._config["audio"] = {}
        self._config["audio"]["save_file_pos"] = "true" if enabled else "false"

    def get_audio_normalize_enabled(self):
        try:
            return self._config.getboolean("audio", "audio_normalize_enabled")
        except (ValueError, configparser.Error):
            return True

    def set_audio_normalize_enabled(self, enabled):
        if "audio" not in self._config:
            self._config["audio"] = {}
        self._config["audio"]["audio_normalize_enabled"] = "true" if enabled else "false"

    def get_audio_mono_enabled(self):
        try:
            return self._config.getboolean("audio", "audio_mono_enabled")
        except (ValueError, configparser.Error):
            return False

    def set_audio_mono_enabled(self, enabled):
        if "audio" not in self._config:
            self._config["audio"] = {}
        self._config["audio"]["audio_mono_enabled"] = "true" if enabled else "false"

    def get_silence_removal_enabled(self):
        self._ensure_silence_removal_section()
        try:
            return self._config.getboolean(SILENCE_REMOVAL_SECTION, "enabled")
        except (ValueError, configparser.Error):
            return False

    def set_silence_removal_enabled(self, enabled):
        self._ensure_silence_removal_section()
        self._config[SILENCE_REMOVAL_SECTION]["enabled"] = "true" if enabled else "false"
        self._cleanup_legacy_silence_keys()

    def get_silence_removal_advanced(self):
        self._ensure_silence_removal_section()
        try:
            return self._config.getboolean(SILENCE_REMOVAL_SECTION, "advanced")
        except (ValueError, configparser.Error):
            return False

    def set_silence_removal_advanced(self, enabled):
        self._ensure_silence_removal_section()
        self._config[SILENCE_REMOVAL_SECTION]["advanced"] = "true" if enabled else "false"

    def get_silence_removal_options(self):
        self._ensure_silence_removal_section()
        options = {}
        for key in SILENCE_REMOVAL_OPTION_KEYS:
            default_value = SILENCE_REMOVAL_DEFAULTS.get(key, "")
            value = self._config.get(SILENCE_REMOVAL_SECTION, key, fallback="")
            if not value:
                value = default_value
            value = (value or "").strip()
            if not value:
                value = default_value
            if key == "threshold":
                value = self._normalize_threshold_value(value)
                if not value:
                    value = SILENCE_REMOVAL_DEFAULTS["threshold"]
            if key == "detection":
                value = value.lower()
                if value not in SILENCE_REMOVAL_DETECTION_MODES:
                    value = SILENCE_REMOVAL_DEFAULTS["detection"]
            options[key] = value
        return options

    def set_silence_removal_options(self, options):
        self._ensure_silence_removal_section()
        options = options or {}
        for key in SILENCE_REMOVAL_OPTION_KEYS:
            value = str(options.get(key, SILENCE_REMOVAL_DEFAULTS.get(key, ""))).strip()
            if not value:
                value = SILENCE_REMOVAL_DEFAULTS.get(key, "")
            if key == "threshold":
                value = self._normalize_threshold_value(value)
                if not value:
                    value = SILENCE_REMOVAL_DEFAULTS["threshold"]
            if key == "detection":
                value = value.lower()
                if value not in SILENCE_REMOVAL_DETECTION_MODES:
                    value = SILENCE_REMOVAL_DEFAULTS["detection"]
            self._config[SILENCE_REMOVAL_SECTION][key] = value
        self._cleanup_legacy_silence_keys()

    def _ensure_silence_removal_section(self):
        if SILENCE_REMOVAL_SECTION not in self._config:
            self._config[SILENCE_REMOVAL_SECTION] = {}

    def _migrate_silence_removal_settings(self, has_new_silence_section):
        self._ensure_silence_removal_section()
        if not self._config.has_section("audio"):
            return

        audio = self._config["audio"]
        silence = self._config[SILENCE_REMOVAL_SECTION]
        if not has_new_silence_section:
            legacy_enabled = str(audio.get("silence_removal_enabled", "")).strip()
            if legacy_enabled:
                silence["enabled"] = legacy_enabled
            for key in SILENCE_REMOVAL_OPTION_KEYS:
                legacy_value = self._get_legacy_silence_option(audio, key)
                if legacy_value:
                    silence[key] = legacy_value
        self._cleanup_legacy_silence_keys()

    def _cleanup_legacy_silence_keys(self):
        if not self._config.has_section("audio"):
            return
        audio = self._config["audio"]
        for key in LEGACY_AUDIO_SILENCE_KEYS:
            audio.pop(key, None)

    def _get_legacy_silence_option(self, audio, key):
        if key == "threshold":
            candidates = (
                audio.get("silence_threshold", ""),
                audio.get("silence_silence_threshold", ""),
                audio.get("silence_start_threshold", ""),
                audio.get("silence_stop_threshold", ""),
            )
            for value in candidates:
                text = self._normalize_threshold_value(value)
                if text:
                    return text
            return ""
        return str(audio.get(f"silence_{key}", "")).strip()

    def _normalize_threshold_value(self, value):
        text = str(value or "").strip()
        if not text:
            return ""
        if text.lower().endswith("db"):
            text = text[:-2].strip()
        return text

    def get_shortcut_overrides(self):
        overrides = {}
        if not self._config.has_section("shortcuts"):
            return overrides
        for action_id, value in self._config.items("shortcuts"):
            shortcut = shortcut_from_config(value)
            if shortcut is not None:
                overrides[action_id] = shortcut
        return overrides

    def set_shortcut_overrides(self, overrides):
        if "shortcuts" not in self._config:
            self._config["shortcuts"] = {}
        else:
            for key in list(self._config["shortcuts"].keys()):
                self._config["shortcuts"].pop(key, None)
        for action_id, shortcut in overrides.items():
            self._config["shortcuts"][action_id] = shortcut_to_config(shortcut)

    def get_secondary_shortcut_overrides(self):
        overrides = {}
        if not self._config.has_section("shortcuts_secondary"):
            return overrides
        for action_id, value in self._config.items("shortcuts_secondary"):
            shortcut = shortcut_from_config(value)
            if shortcut is not None:
                overrides[action_id] = shortcut
        return overrides

    def set_secondary_shortcut_overrides(self, overrides):
        if "shortcuts_secondary" not in self._config:
            self._config["shortcuts_secondary"] = {}
        else:
            for key in list(self._config["shortcuts_secondary"].keys()):
                self._config["shortcuts_secondary"].pop(key, None)
        for action_id, shortcut in overrides.items():
            self._config["shortcuts_secondary"][action_id] = shortcut_to_config(shortcut)

    def get_global_shortcut_overrides(self):
        overrides = {}
        if not self._config.has_section("global_shortcuts"):
            return overrides
        for action_id, value in self._config.items("global_shortcuts"):
            shortcut = shortcut_from_config(value)
            if shortcut is not None:
                overrides[action_id] = shortcut
        return overrides

    def set_global_shortcut_overrides(self, overrides):
        if "global_shortcuts" not in self._config:
            self._config["global_shortcuts"] = {}
        else:
            for key in list(self._config["global_shortcuts"].keys()):
                self._config["global_shortcuts"].pop(key, None)
        for action_id, shortcut in overrides.items():
            self._config["global_shortcuts"][action_id] = shortcut_to_config(shortcut)
