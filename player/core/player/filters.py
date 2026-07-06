from config.settings_manager import SILENCE_REMOVAL_DEFAULTS


class PlayerFiltersMixin:
    def set_audio_normalize_enabled(self, enabled):
        previous = self._audio_normalize_enabled
        self._audio_normalize_enabled = bool(enabled)
        if self._engine.set_audio_normalize_filter(self._audio_normalize_enabled):
            return True
        self._audio_normalize_enabled = previous
        self._engine.set_audio_normalize_filter(self._audio_normalize_enabled)
        return False

    def is_audio_normalize_enabled(self):
        return self._audio_normalize_enabled

    def set_audio_mono_enabled(self, enabled):
        previous = self._audio_mono_enabled
        self._audio_mono_enabled = bool(enabled)
        if self._state.current_path:
            if self._apply_mono_filter():
                return True
            self._audio_mono_enabled = previous
            self._apply_mono_filter()
            return False
        return True

    def is_audio_mono_enabled(self):
        return self._audio_mono_enabled

    def configure_silence_removal(self, options):
        self._silence_removal_options = dict(options or {})
        if self._silence_removal_enabled and self._state.current_path:
            return self._apply_silence_removal_filter()
        return True

    def is_silence_removal_enabled(self):
        return self._silence_removal_enabled

    def set_silence_removal_enabled(self, enabled):
        previous = self._silence_removal_enabled
        self._silence_removal_enabled = bool(enabled)
        if self._state.current_path:
            if self._apply_silence_removal_filter():
                return True
            self._silence_removal_enabled = previous
            self._apply_silence_removal_filter()
            return False
        return True

    def toggle_silence_removal(self):
        next_value = not self._silence_removal_enabled
        success = self.set_silence_removal_enabled(next_value)
        if not success:
            return self._silence_removal_enabled, False
        return next_value, True

    def _apply_silence_removal_filter(self):
        graph = self._build_silence_filter_graph()
        return self._engine.set_silence_removal_filter(
            self._silence_removal_enabled,
            graph,
        )

    def _apply_mono_filter(self):
        return self._engine.set_mono_filter(self._audio_mono_enabled)

    def _apply_active_audio_filters(self):
        self._apply_silence_removal_filter()
        self._apply_mono_filter()

    def _build_silence_filter_graph(self):
        threshold = str(
            self._silence_removal_options.get(
                "threshold",
                SILENCE_REMOVAL_DEFAULTS["threshold"],
            )
        ).strip()
        if not threshold:
            threshold = str(self._silence_removal_options.get("silence_threshold", "")).strip()
        if not threshold:
            threshold = str(self._silence_removal_options.get("start_threshold", "")).strip()
        if not threshold:
            threshold = str(self._silence_removal_options.get("stop_threshold", "")).strip()
        if not threshold:
            threshold = SILENCE_REMOVAL_DEFAULTS["threshold"]
        threshold = self._format_silence_threshold(threshold)

        def option(key):
            return self._silence_removal_options.get(
                key,
                SILENCE_REMOVAL_DEFAULTS.get(key, ""),
            )

        fields = (
            ("start_periods", option("start_periods")),
            ("start_duration", option("start_duration")),
            ("start_threshold", threshold),
            ("stop_periods", option("stop_periods")),
            ("stop_duration", option("stop_duration")),
            ("stop_threshold", threshold),
            ("stop_silence", option("stop_silence")),
            ("window", option("window")),
            ("detection", option("detection")),
        )
        parts = []
        for key, raw_value in fields:
            value = str(raw_value).strip()
            if value:
                parts.append(f"{key}={value}")
        return "silenceremove=" + ":".join(parts)

    def _format_silence_threshold(self, value):
        text = str(value or "").strip()
        if not text:
            text = SILENCE_REMOVAL_DEFAULTS["threshold"]
        if text.lower().endswith("db"):
            text = text[:-2].strip()
        if not text:
            text = SILENCE_REMOVAL_DEFAULTS["threshold"]
        return f"{text}dB"
