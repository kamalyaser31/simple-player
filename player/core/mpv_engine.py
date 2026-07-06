import os

import mpv

from config.constants import SPEED_MAX, SPEED_MIN, VOLUME_MAX, VOLUME_MIN
from helpers.utils import clamp

SILENCE_FILTER_LABEL = "@silenceremove"
AUDIO_PREAMP_FILTER_LABEL = "@audiopreamp"
AUDIO_NORMALIZE_FILTER_LABEL = "@audionormalize"
AUDIO_MONO_FILTER_LABEL = "@audiomono"
AUDIO_NORMALIZE_FILTER_GRAPH = "dynaudnorm=f=150:g=15,alimiter=limit=0.95"
AUDIO_MONO_FILTER_GRAPH = "aformat=channel_layouts=mono"
BASE_VOLUME = 100.0
HIGH_VOLUME_PREAMP = max(1.0, VOLUME_MAX / BASE_VOLUME)
NETWORK_TIMEOUT_SECONDS = 10
MEDIA_CONTROLS_OPTION = "media-controls"
MEDIA_KEYS_OPTION = "input-media-keys"


class MpvEngine:
    def __init__(self, on_end_file=None):
        self._on_end_file = on_end_file
        self._mpv = self._create_core()
        self._test_mpv = None
        self._test_end_handler = None
        self._audio_normalize_enabled = False
        self._audio_mono_enabled = False
        self._requested_volume = BASE_VOLUME
        self._apply_network_defaults()
        self._apply_windows_media_defaults()
        self._register_event_handlers()

    def _create_core(self, window_id=None):
        options = self._create_core_options(window_id)
        return mpv.MPV(**options)

    def _create_core_options(self, window_id=None):
        options = {
            "vo": "gpu",
            "osc": False,
            "keep_open": "no",
            "input_default_bindings": False,
            "input_vo_keyboard": False,
        }
        if window_id:
            options["wid"] = str(window_id)
        return options

    def _apply_network_defaults(self):
        # Prevent indefinite hangs on broken network streams.
        try:
            self._mpv["network-timeout"] = NETWORK_TIMEOUT_SECONDS
            return
        except Exception:
            pass
        try:
            self._mpv.command("set", "network-timeout", str(NETWORK_TIMEOUT_SECONDS))
        except Exception:
            pass

    def _apply_windows_media_defaults(self):
        # The app-owned WindowsMediaBridge handles SMTC/status to avoid duplicate owners.
        if os.name != "nt":
            return
        self._set_option_safe(MEDIA_CONTROLS_OPTION, "no")
        self._set_option_safe(MEDIA_KEYS_OPTION, "no")

    def _set_option_safe(self, name, value):
        try:
            self._mpv[str(name)] = value
            return
        except Exception:
            pass
        try:
            self._mpv.command("set", str(name), str(value))
        except Exception:
            pass

    def _register_event_handlers(self):
        @self._mpv.event_callback("end-file")
        def _on_end_file(event):
            if self._on_end_file is not None:
                self._on_end_file(event)

        self._end_file_handler = _on_end_file

    def terminate(self):
        self.stop_test_sound()
        try:
            self._mpv.terminate()
        except Exception:
            pass

    def try_set_window_id(self, window_id):
        try:
            self._mpv["wid"] = str(window_id)
            return True
        except Exception:
            return False

    def recreate_with_window(self, window_id):
        snapshot = self.snapshot_runtime_state()
        old_mpv = self._mpv
        try:
            self._mpv = self._create_core(window_id)
        except Exception:
            self._mpv = old_mpv
            return None
        self._apply_network_defaults()
        self._apply_windows_media_defaults()
        self.set_audio_normalize_filter(self._audio_normalize_enabled)
        self.set_mono_filter(self._audio_mono_enabled)
        self._register_event_handlers()
        try:
            old_mpv.terminate()
        except Exception:
            pass
        return snapshot

    def snapshot_runtime_state(self):
        return {
            "volume": self.get_volume(),
            "speed": self.get_speed(),
            "audio_device": self.get_audio_device(),
            "paused": self.is_paused(),
            "resume_at": self.get_elapsed(),
        }

    def restore_runtime_state(self, snapshot):
        if not isinstance(snapshot, dict):
            return
        volume = snapshot.get("volume")
        speed = snapshot.get("speed")
        audio_device = snapshot.get("audio_device")
        if volume is not None:
            self.set_volume(volume)
        if speed is not None:
            self.set_speed(speed)
        if audio_device:
            self.set_audio_device(audio_device)

    def load_file(self, path, start_position=None, paused=False):
        self._ensure_audio_device_available()
        try:
            if start_position is not None:
                self._mpv.loadfile(path, "replace", start=start_position)
            else:
                self._mpv.play(path)
            self._mpv.pause = bool(paused)
            return True
        except Exception:
            return False

    def stop(self):
        try:
            self._mpv.command("stop")
        except Exception:
            pass

    def toggle_pause(self):
        paused = bool(self._mpv.pause)
        if paused:
            self._ensure_audio_device_available()
        self._mpv.pause = not paused
        return not self._mpv.pause

    def play(self):
        self._ensure_audio_device_available()
        self._mpv.pause = False

    def pause(self):
        self._mpv.pause = True

    def is_paused(self):
        try:
            return bool(self._mpv.pause)
        except Exception:
            return False

    def seek_relative(self, seconds):
        try:
            self._mpv.command("seek", seconds, "relative")
        except Exception:
            pass

    def seek_absolute(self, seconds):
        try:
            self._mpv.command("seek", seconds, "absolute")
        except Exception:
            pass

    def seek_absolute_exact(self, seconds):
        try:
            self._mpv.command("seek", seconds, "absolute+exact")
        except Exception:
            pass

    def set_volume(self, volume):
        volume = float(clamp(volume, VOLUME_MIN, VOLUME_MAX))
        self._requested_volume = volume

        if not self._audio_normalize_enabled:
            self._mpv.volume = volume
            return volume

        if volume <= BASE_VOLUME:
            self._set_preamp_gain(1.0)
            self._mpv.volume = volume
            return volume

        # Continuous mapping above 100%: keep mpv at 100 and scale preamp smoothly.
        preamp_gain = min(HIGH_VOLUME_PREAMP, volume / BASE_VOLUME)
        self._set_preamp_gain(preamp_gain)
        self._mpv.volume = BASE_VOLUME
        return volume

    def get_volume(self):
        return clamp(self._requested_volume, VOLUME_MIN, VOLUME_MAX)

    def set_speed(self, speed):
        speed = clamp(speed, SPEED_MIN, SPEED_MAX)
        self._mpv.speed = speed
        return speed

    def get_speed(self):
        try:
            speed = float(self._mpv.speed)
        except Exception:
            speed = 1.0
        return clamp(speed, SPEED_MIN, SPEED_MAX)

    def set_end_behavior(self, behavior):
        try:
            self._mpv.keep_open = "yes" if behavior == "none" else "no"
        except Exception:
            pass
        try:
            self._mpv.loop_file = "inf" if behavior == "loop" else "no"
        except Exception:
            pass

    def get_audio_devices(self):
        try:
            devices = self._mpv.audio_device_list
        except Exception:
            return []
        results = []
        if isinstance(devices, list):
            for entry in devices:
                if isinstance(entry, dict):
                    name = entry.get("name")
                    desc = entry.get("description") or entry.get("label") or name
                    if name:
                        results.append((name, desc or name))
                elif isinstance(entry, str):
                    results.append((entry, entry))
        return results

    def set_audio_device(self, device_name):
        target = str(device_name or "").strip() or "auto"
        if target != "auto" and not self._is_audio_device_available(target):
            return self._fallback_audio_device()
        try:
            self._mpv.audio_device = target
            return True
        except Exception:
            return False

    def get_audio_device(self):
        try:
            return self._mpv.audio_device
        except Exception:
            return ""

    def set_loop_start(self, seconds):
        try:
            self._mpv["ab-loop-a"] = seconds
            self._mpv["ab-loop-b"] = "no"
            return True
        except Exception:
            return False

    def set_loop_end(self, seconds):
        try:
            self._mpv["ab-loop-b"] = seconds
            return True
        except Exception:
            return False

    def clear_loop(self):
        try:
            self._mpv["ab-loop-a"] = "no"
            self._mpv["ab-loop-b"] = "no"
            return True
        except Exception:
            return False

    def get_elapsed(self):
        return getattr(self._mpv, "time_pos", None)

    def get_remaining(self):
        return getattr(self._mpv, "time_remaining", None)

    def get_duration(self):
        return getattr(self._mpv, "duration", None)

    def set_silence_removal_filter(self, enabled, filter_graph):
        if not self._remove_filter_by_label(SILENCE_FILTER_LABEL):
            return False
        if not enabled:
            return True
        if not filter_graph:
            return False
        entry = f"{SILENCE_FILTER_LABEL}:lavfi=[{filter_graph}]"
        try:
            self._mpv.command("af", "add", entry)
            return True
        except Exception:
            return False

    def set_audio_normalize_filter(self, enabled):
        self._audio_normalize_enabled = bool(enabled)
        self._remove_filter_by_label(AUDIO_PREAMP_FILTER_LABEL)
        self._remove_filter_by_label(AUDIO_NORMALIZE_FILTER_LABEL)
        if not self._audio_normalize_enabled:
            self._mpv.volume = self._requested_volume
            return True

        preamp_entry = f"{AUDIO_PREAMP_FILTER_LABEL}:lavfi=[volume=1.0]"
        normalize_entry = (
            f"{AUDIO_NORMALIZE_FILTER_LABEL}:lavfi=[{AUDIO_NORMALIZE_FILTER_GRAPH}]"
        )
        try:
            self._mpv.command("af", "add", preamp_entry)
            self._mpv.command("af", "add", normalize_entry)
        except Exception:
            self._remove_filter_by_label(AUDIO_PREAMP_FILTER_LABEL)
            self._remove_filter_by_label(AUDIO_NORMALIZE_FILTER_LABEL)
            return False

        # Re-apply requested volume using preamp-aware mapping.
        self.set_volume(self._requested_volume)
        return True

    def set_mono_filter(self, enabled):
        self._audio_mono_enabled = bool(enabled)
        self._remove_filter_by_label(AUDIO_MONO_FILTER_LABEL)
        if not self._audio_mono_enabled:
            return True
        entry = f"{AUDIO_MONO_FILTER_LABEL}:lavfi=[{AUDIO_MONO_FILTER_GRAPH}]"
        try:
            self._mpv.command("af", "add", entry)
            return True
        except Exception:
            return False

    def _set_preamp_gain(self, gain):
        if not self._audio_normalize_enabled:
            return True
        entry = f"{AUDIO_PREAMP_FILTER_LABEL}:lavfi=[volume={gain:.3f}]"
        self._remove_filter_by_label(AUDIO_PREAMP_FILTER_LABEL)
        try:
            self._mpv.command("af", "add", entry)
            return True
        except Exception:
            return False

    def _remove_filter_by_label(self, label):
        try:
            self._mpv.command("af", "remove", label)
        except Exception:
            pass
        return True

    def play_test_sound(self, path):
        self.stop_test_sound()
        self._ensure_audio_device_available()
        options = {
            "vid": "no",
            "vo": "null",
            "keep_open": "no",
            "input_default_bindings": False,
            "input_vo_keyboard": False,
            "osc": False,
        }
        device = self.get_audio_device()
        if device:
            options["audio_device"] = device
        try:
            test_mpv = mpv.MPV(**options)
        except Exception:
            return False

        @test_mpv.event_callback("end-file")
        def _on_test_end(_event):
            self.stop_test_sound()

        self._test_end_handler = _on_test_end
        self._test_mpv = test_mpv
        try:
            self._test_mpv.command("loadfile", path, "replace")
            self._test_mpv.pause = False
            return True
        except Exception:
            self.stop_test_sound()
            return False

    def stop_test_sound(self):
        test_mpv = self._test_mpv
        self._test_mpv = None
        self._test_end_handler = None
        if test_mpv is None:
            return
        try:
            test_mpv.terminate()
        except Exception:
            pass

    def _ensure_audio_device_available(self):
        current = str(self.get_audio_device() or "").strip()
        if self._is_audio_device_available(current):
            return True
        return self._fallback_audio_device()

    def _is_audio_device_available(self, device_name):
        target = str(device_name or "").strip()
        if not target or target == "auto":
            return True
        for name, _desc in self.get_audio_devices():
            if str(name or "").strip() == target:
                return True
        return False

    def _fallback_audio_device(self):
        try:
            self._mpv.audio_device = "auto"
            return True
        except Exception:
            return False

