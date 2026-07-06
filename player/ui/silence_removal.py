import wx
from gettext import gettext as _

from config.settings_manager import (
    SILENCE_REMOVAL_DEFAULTS,
    SILENCE_REMOVAL_DETECTION_MODES,
)


MIN_DURATION_HINT = _(
    "Minimum silence duration in seconds. "
    "Silence shorter than this is kept. "
    "Default is 0.5."
)

THRESHOLD_HINT = _(
    "Silence level threshold. "
    "Audio below this level is treated as silence. Enter only a number, for example -30."
)

ADVANCED_TEXT_FIELDS = [
    (
        "start_periods",
        _("Leading silent parts to trim"),
        _("How many silent chunks to remove from the beginning."),
    ),
    (
        "start_duration",
        _("Minimum leading silence length (seconds)"),
        _("Only trim leading silence chunks that are at least this long (default: 0.2)."),
    ),
    (
        "stop_periods",
        _("Silent parts to trim after audio starts"),
        _("How many silence chunks to trim after audio has started (-1 means all)."),
    ),
    (
        "stop_duration",
        _("Minimum inner silence length (seconds)"),
        _("Only trim middle/end silence chunks that are at least this long."),
    ),
    (
        "stop_silence",
        _("Pause to keep after trimmed silence (seconds)"),
        _("Leaves a short pause before the next word (default: 0.2)."),
    ),
    (
        "window",
        _("Detection window size (seconds)"),
        _("Smoothing window used by silence detection (default: 0.02)."),
    ),
]
ADVANCED_TEXT_LABELS = {key: label for key, label, _hint in ADVANCED_TEXT_FIELDS}

DETECTION_HINT = _(
    "How silence is detected. Peak reacts faster to speech transients (default). "
    "RMS is smoother and less sensitive to short spikes."
)

SILENCE_DETECTION_LABELS = {
    "peak": _("Peak (fast reaction)"),
    "rms": _("RMS (smoother)"),
}


class SilenceRemovalSettings(wx.ScrolledWindow):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self._settings = settings
        self._advanced_controls = {}
        self._help_map = {}
        self.SetScrollRate(8, 8)

        silence_group = wx.StaticBoxSizer(
            wx.VERTICAL, self, _("Silence removal (FFmpeg silenceremove)")
        )
        silence_options = self._settings.get_silence_removal_options()

        basic_grid = wx.FlexGridSizer(cols=2, vgap=6, hgap=8)
        basic_grid.AddGrowableCol(1, 1)

        min_duration_label = wx.StaticText(self, label=_("Minimum silence duration (seconds)"))
        min_duration_label.SetToolTip(MIN_DURATION_HINT)
        self._min_duration_field = wx.TextCtrl(
            self,
            value=self._initial_minimum_duration(silence_options),
        )
        self._min_duration_field.SetToolTip(MIN_DURATION_HINT)
        self._help_map[self._min_duration_field] = lambda: self._help_silence_field(
            "minimum_duration"
        )
        basic_grid.Add(min_duration_label, 0, wx.ALIGN_CENTER_VERTICAL)
        basic_grid.Add(self._min_duration_field, 1, wx.EXPAND)

        threshold_label = wx.StaticText(self, label=_("Silence threshold"))
        threshold_label.SetToolTip(THRESHOLD_HINT)
        threshold_value = silence_options.get("threshold", SILENCE_REMOVAL_DEFAULTS["threshold"])
        self._threshold_field = wx.TextCtrl(self, value=str(threshold_value))
        self._threshold_field.SetToolTip(THRESHOLD_HINT)
        self._help_map[self._threshold_field] = lambda: self._help_silence_field("threshold")
        basic_grid.Add(threshold_label, 0, wx.ALIGN_CENTER_VERTICAL)
        basic_grid.Add(self._threshold_field, 1, wx.EXPAND)

        silence_group.Add(basic_grid, 0, wx.EXPAND | wx.ALL, 8)

        self._advanced_checkbox = wx.CheckBox(self, label=_("Show advanced settings"))
        self._advanced_checkbox.SetValue(self._settings.get_silence_removal_advanced())
        self._help_map[self._advanced_checkbox] = lambda: self._help_silence_field("advanced")
        self._advanced_checkbox.Bind(wx.EVT_CHECKBOX, self._on_toggle_advanced)
        silence_group.Add(self._advanced_checkbox, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self._advanced_panel = wx.Panel(self)
        advanced_grid = wx.FlexGridSizer(cols=2, vgap=6, hgap=8)
        advanced_grid.AddGrowableCol(1, 1)
        for key, label, hint in ADVANCED_TEXT_FIELDS:
            title = wx.StaticText(self._advanced_panel, label=label)
            title.SetToolTip(hint)
            value = silence_options.get(key, SILENCE_REMOVAL_DEFAULTS.get(key, ""))
            field = wx.TextCtrl(self._advanced_panel, value=str(value))
            field.SetToolTip(hint)
            advanced_grid.Add(title, 0, wx.ALIGN_CENTER_VERTICAL)
            advanced_grid.Add(field, 1, wx.EXPAND)
            self._advanced_controls[key] = field
            self._help_map[field] = lambda key=key: self._help_silence_field(key)

        detection_label = wx.StaticText(self._advanced_panel, label=_("Detection mode"))
        detection_label.SetToolTip(DETECTION_HINT)
        detection_choices = [
            SILENCE_DETECTION_LABELS.get(mode, mode) for mode in SILENCE_REMOVAL_DETECTION_MODES
        ]
        self._detection_choice = wx.Choice(self._advanced_panel, choices=detection_choices)
        detection_mode = str(
            silence_options.get("detection", SILENCE_REMOVAL_DEFAULTS["detection"])
        ).strip().lower()
        try:
            detection_index = SILENCE_REMOVAL_DETECTION_MODES.index(detection_mode)
        except ValueError:
            detection_index = SILENCE_REMOVAL_DETECTION_MODES.index(
                SILENCE_REMOVAL_DEFAULTS["detection"]
            )
        self._detection_choice.SetSelection(detection_index)
        self._detection_choice.SetToolTip(DETECTION_HINT)
        self._help_map[self._detection_choice] = lambda: self._help_silence_field("detection")
        advanced_grid.Add(detection_label, 0, wx.ALIGN_CENTER_VERTICAL)
        advanced_grid.Add(self._detection_choice, 1, wx.EXPAND)

        advanced_sizer = wx.BoxSizer(wx.VERTICAL)
        advanced_sizer.Add(advanced_grid, 1, wx.EXPAND)
        self._advanced_panel.SetSizer(advanced_sizer)
        silence_group.Add(self._advanced_panel, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)

        root_sizer = wx.BoxSizer(wx.VERTICAL)
        root_sizer.Add(silence_group, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP | wx.EXPAND, 8)
        self.SetSizer(root_sizer)
        self._set_advanced_visibility(self._advanced_checkbox.GetValue())

    def apply(self):
        silence_options = self._settings.get_silence_removal_options()
        minimum_duration = self._min_duration_field.GetValue().strip()
        if not minimum_duration:
            minimum_duration = SILENCE_REMOVAL_DEFAULTS["stop_duration"]
        threshold = self._threshold_field.GetValue().strip()
        if not threshold:
            threshold = SILENCE_REMOVAL_DEFAULTS["threshold"]

        silence_options["threshold"] = threshold
        advanced = self._advanced_checkbox.GetValue()
        if advanced:
            for key, _label, _hint in ADVANCED_TEXT_FIELDS:
                control = self._advanced_controls.get(key)
                value = control.GetValue().strip() if control is not None else ""
                if not value:
                    if key == "stop_duration":
                        value = minimum_duration
                    else:
                        value = str(silence_options.get(key, "")).strip()
                        if not value:
                            value = SILENCE_REMOVAL_DEFAULTS.get(key, "")
                silence_options[key] = value
            selection = self._detection_choice.GetSelection()
            if selection == wx.NOT_FOUND:
                selection = SILENCE_REMOVAL_DETECTION_MODES.index(
                    SILENCE_REMOVAL_DEFAULTS["detection"]
                )
            silence_options["detection"] = SILENCE_REMOVAL_DETECTION_MODES[selection]
        else:
            # Keep hidden advanced values as configured; only update the basic fields.
            silence_options["stop_duration"] = minimum_duration
            if not str(silence_options.get("start_duration", "")).strip():
                silence_options["start_duration"] = SILENCE_REMOVAL_DEFAULTS["start_duration"]
            for key in ("start_periods", "stop_periods", "stop_silence", "window", "detection"):
                if not str(silence_options.get(key, "")).strip():
                    silence_options[key] = SILENCE_REMOVAL_DEFAULTS[key]

        self._settings.set_silence_removal_options(silence_options)
        self._settings.set_silence_removal_advanced(advanced)

    def validate_inputs(self):
        min_duration = self._min_duration_field.GetValue().strip()
        if min_duration:
            ok, parsed = self._parse_float(min_duration)
            if not ok or parsed < 0:
                self._min_duration_field.SetFocus()
                return _("Minimum silence duration must be a non-negative number.")

        threshold = self._threshold_field.GetValue().strip()
        if threshold:
            ok, _parsed = self._parse_float(threshold)
            if not ok:
                self._threshold_field.SetFocus()
                return _("Silence threshold must be a valid number.")

        if not self._advanced_checkbox.GetValue():
            return ""

        for key, _label, _hint in ADVANCED_TEXT_FIELDS:
            control = self._advanced_controls.get(key)
            if control is None:
                continue
            text = control.GetValue().strip()
            if not text:
                continue

            if key in ("start_periods", "stop_periods"):
                ok, parsed = self._parse_int(text)
                if not ok:
                    control.SetFocus()
                    return _("{field} must be an integer value.").format(
                        field=ADVANCED_TEXT_LABELS.get(key, key)
                    )
                if key == "start_periods" and parsed < 0:
                    control.SetFocus()
                    return _("{field} must be zero or greater.").format(
                        field=ADVANCED_TEXT_LABELS.get(key, key)
                    )
                if key == "stop_periods" and parsed < -1:
                    control.SetFocus()
                    return _("{field} must be -1 or greater.").format(
                        field=ADVANCED_TEXT_LABELS.get(key, key)
                    )
                continue

            ok, parsed = self._parse_float(text)
            if not ok or parsed < 0:
                control.SetFocus()
                return _("{field} must be a non-negative number.").format(
                    field=ADVANCED_TEXT_LABELS.get(key, key)
                )
        return ""

    def refresh_from_settings(self):
        silence_options = self._settings.get_silence_removal_options()
        self._min_duration_field.SetValue(self._initial_minimum_duration(silence_options))
        threshold_value = silence_options.get("threshold", SILENCE_REMOVAL_DEFAULTS["threshold"])
        self._threshold_field.SetValue(str(threshold_value))
        for key, _label, _hint in ADVANCED_TEXT_FIELDS:
            field = self._advanced_controls.get(key)
            if field is None:
                continue
            field.SetValue(str(silence_options.get(key, SILENCE_REMOVAL_DEFAULTS.get(key, ""))))
        detection_mode = str(
            silence_options.get("detection", SILENCE_REMOVAL_DEFAULTS["detection"])
        ).strip().lower()
        try:
            detection_index = SILENCE_REMOVAL_DETECTION_MODES.index(detection_mode)
        except ValueError:
            detection_index = SILENCE_REMOVAL_DETECTION_MODES.index(
                SILENCE_REMOVAL_DEFAULTS["detection"]
            )
        self._detection_choice.SetSelection(detection_index)
        advanced = self._settings.get_silence_removal_advanced()
        self._advanced_checkbox.SetValue(advanced)
        self._set_advanced_visibility(advanced)

    def get_context_help(self, focused):
        control = focused
        while control is not None:
            if control in self._help_map:
                return self._help_map[control]()
            if control is self:
                break
            control = control.GetParent()
        return _(
            "Silence removal settings. Minimum silence duration and threshold are always shown. "
            "Enable advanced settings to configure all remaining filter options."
        )

    def _on_toggle_advanced(self, _event):
        self._set_advanced_visibility(self._advanced_checkbox.GetValue())

    def _set_advanced_visibility(self, visible):
        self._advanced_panel.Show(bool(visible))
        self.Layout()
        self.FitInside()

    def _initial_minimum_duration(self, silence_options):
        stop_duration = str(silence_options.get("stop_duration", "")).strip()
        start_duration = str(silence_options.get("start_duration", "")).strip()
        if stop_duration:
            return stop_duration
        if start_duration:
            return start_duration
        return SILENCE_REMOVAL_DEFAULTS["stop_duration"]

    def _help_silence_field(self, key):
        if key == "minimum_duration":
            return _(
                "Minimum silence duration in seconds. "
                "Silence shorter than this value is kept. "
                "Increase it to preserve short pauses. "
                "Decrease it to trim more aggressively."
            )
        if key == "threshold":
            return _(
                "Silence level threshold. "
                "Audio quieter than this level is treated as silence. "
                "Enter only the number, for example -20, -30, or -40."
            )
        if key == "advanced":
            return _(
                "Show advanced settings. "
                "When enabled, extra silenceremove parameters are displayed. "
                "When disabled, only minimum duration and threshold are used."
            )
        if key == "start_periods":
            return _(
                "Leading silent parts to trim. "
                "This controls how many silent chunks are removed from the beginning. "
                "Typical value is 1."
            )
        if key == "start_duration":
            return _(
                "Minimum leading silence length in seconds. "
                "Only leading silence at least this long is removed. "
                "Default is 0.2."
            )
        if key == "stop_periods":
            return _(
                "Silent parts to trim after audio starts. "
                "Use -1 to trim all matching silent parts."
            )
        if key == "stop_duration":
            return _(
                "Minimum inner silence length in seconds. "
                "Only silence in the middle or end at least this long is removed."
            )
        if key == "stop_silence":
            return _(
                "Pause to keep after trimmed silence, in seconds. "
                "Default is 0.2."
            )
        if key == "window":
            return _(
                "Detection window size in seconds. "
                "Default is 0.02."
            )
        if key == "detection":
            return _(
                "Detection mode for silence analysis. "
                "Peak reacts quickly to speech transients. "
                "RMS is smoother."
            )
        return _("Silence removal setting. Enter a value and press OK to save.")

    def _parse_float(self, text):
        try:
            return True, float(str(text).strip())
        except (TypeError, ValueError):
            return False, 0.0

    def _parse_int(self, text):
        try:
            return True, int(str(text).strip())
        except (TypeError, ValueError):
            return False, 0

