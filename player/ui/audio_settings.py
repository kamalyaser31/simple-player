import wx
from gettext import gettext as _


END_BEHAVIOR_LABELS = [
    _("Advance to the next file"),
    _("Loop the file"),
    _("Do nothing"),
]
END_BEHAVIOR_VALUES = ["advance", "loop", "none"]


class AudioSettings(wx.ScrolledWindow):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self._settings = settings
        self._help_map = {}
        self.SetScrollRate(8, 8)

        self._custom_label = wx.StaticText(
            self, label=_("Custom seek value (seconds)")
        )
        self._custom_value = wx.TextCtrl(self)
        self._custom_value.SetValue(str(self._settings.get_seek_step_custom()))
        self._help_map[self._custom_value] = self._help_custom_seek

        self._speed_step_label = wx.StaticText(self, label=_("Speed step"))
        self._speed_step_value = wx.TextCtrl(self)
        self._speed_step_value.SetValue(str(self._settings.get_speed_step()))
        self._help_map[self._speed_step_value] = self._help_speed_step

        self._volume_step_label = wx.StaticText(self, label=_("Volume step"))
        self._volume_step_value = wx.SpinCtrl(self, min=1, max=20)
        self._volume_step_value.SetValue(self._settings.get_volume_step())
        self._help_map[self._volume_step_value] = self._help_volume_step

        self._end_label = wx.StaticText(self, label=_("What happens after a file ends?"))
        self._end_choice = wx.Choice(self, choices=END_BEHAVIOR_LABELS)
        current_behavior = self._settings.get_end_behavior()
        try:
            index = END_BEHAVIOR_VALUES.index(current_behavior)
        except ValueError:
            index = 0
        self._end_choice.SetSelection(index)
        self._help_map[self._end_choice] = self._help_end_behavior

        self._wrap_playlist_checkbox = wx.CheckBox(
            self, label=_("Wrap to top for multiple files")
        )
        self._wrap_playlist_checkbox.SetValue(self._settings.get_wrap_playlist())
        self._help_map[self._wrap_playlist_checkbox] = self._help_wrap_playlist

        self._save_file_pos_checkbox = wx.CheckBox(
            self, label=_("Save current position for each file")
        )
        self._save_file_pos_checkbox.SetValue(self._settings.get_save_file_pos())
        self._help_map[self._save_file_pos_checkbox] = self._help_save_file_pos

        self._normalize_checkbox = wx.CheckBox(
            self, label=_("Enable dynamic normalize and limiter")
        )
        self._normalize_checkbox.SetValue(self._settings.get_audio_normalize_enabled())
        self._help_map[self._normalize_checkbox] = self._help_normalize_filter

        self._mono_checkbox = wx.CheckBox(
            self, label=_("Play audio as Mono")
        )
        self._mono_checkbox.SetValue(self._settings.get_audio_mono_enabled())
        self._help_map[self._mono_checkbox] = self._help_mono_filter

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._custom_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        sizer.Add(self._custom_value, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        sizer.Add(self._speed_step_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        sizer.Add(self._speed_step_value, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        sizer.Add(self._volume_step_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        sizer.Add(self._volume_step_value, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        sizer.Add(self._end_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        sizer.Add(self._end_choice, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        sizer.Add(self._wrap_playlist_checkbox, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        sizer.Add(self._save_file_pos_checkbox, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        sizer.Add(self._normalize_checkbox, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        sizer.Add(self._mono_checkbox, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        self.SetSizer(sizer)

    def validate_inputs(self):
        text = self._speed_step_value.GetValue().strip()
        try:
            value = float(text)
            if value <= 0:
                raise ValueError
        except ValueError:
            self._speed_step_value.SetFocus()
            return _("Speed step must be a positive number.")
        return ""

    def apply(self):
        text = self._custom_value.GetValue().strip()
        try:
            value = float(text)
            if value <= 0:
                raise ValueError
        except ValueError:
            value = self._settings.get_seek_step_custom()
        self._settings.set_seek_step_custom(value)
        self._settings.set_speed_step(self._speed_step_value.GetValue().strip())
        self._settings.set_volume_step(self._volume_step_value.GetValue())
        selection = self._end_choice.GetSelection()
        if selection == wx.NOT_FOUND:
            selection = 0
        self._settings.set_end_behavior(END_BEHAVIOR_VALUES[selection])
        self._settings.set_wrap_playlist(self._wrap_playlist_checkbox.GetValue())
        self._settings.set_save_file_pos(self._save_file_pos_checkbox.GetValue())
        self._settings.set_audio_normalize_enabled(self._normalize_checkbox.GetValue())
        self._settings.set_audio_mono_enabled(self._mono_checkbox.GetValue())

    def refresh_from_settings(self):
        self._custom_value.SetValue(str(self._settings.get_seek_step_custom()))
        self._speed_step_value.SetValue(str(self._settings.get_speed_step()))
        self._volume_step_value.SetValue(self._settings.get_volume_step())
        current_behavior = self._settings.get_end_behavior()
        try:
            index = END_BEHAVIOR_VALUES.index(current_behavior)
        except ValueError:
            index = 0
        self._end_choice.SetSelection(index)
        self._wrap_playlist_checkbox.SetValue(self._settings.get_wrap_playlist())
        self._save_file_pos_checkbox.SetValue(self._settings.get_save_file_pos())
        self._normalize_checkbox.SetValue(self._settings.get_audio_normalize_enabled())
        self._mono_checkbox.SetValue(self._settings.get_audio_mono_enabled())

    def get_context_help(self, focused):
        control = focused
        while control is not None:
            if control in self._help_map:
                return self._help_map[control]()
            if control is self:
                break
            control = control.GetParent()
        return _(
            "Audio settings. Use Tab to move between controls. "
            "Press F1 on a specific control to hear detailed help."
        )

    def _help_custom_seek(self):
        return _(
            "Custom seek value in seconds. "
            "This value is used when the custom seek step is selected. "
            "Enter a positive number like 5, 10, or 30. "
            "Decimals are allowed, for example 2.5 seconds."
        )

    def _help_end_behavior(self):
        return _(
            "What happens after a file ends. "
            "Advance to the next file moves to the next item in the playlist. "
            "Loop the file repeats the same file automatically. "
            "Do nothing keeps playback stopped at the end. "
            "Possible values: Advance to the next file, Loop the file, or Do nothing."
        )

    def _help_speed_step(self):
        return _(
            "Speed step used when increasing or decreasing playback speed. "
            "Enter a positive decimal value like 0.025 or 0.1."
        )

    def _help_wrap_playlist(self):
        return _(
            "Wrap to top for multiple files. "
            "When enabled and the playlist has more than one file, moving next from the last file goes to the first file, "
            "and moving previous from the first file goes to the last file. "
            "Advance-at-end uses the same wrapping behavior."
        )

    def _help_save_file_pos(self):
        return _(
            "Save current position for each file. "
            "When enabled, the app stores the current position of files and restores that position when navigating between files."
        )

    def _help_volume_step(self):
        return _(
            "Volume step used when pressing volume up or down. "
            "Allowed range is from 1 to 20."
        )

    def _help_normalize_filter(self):
        return _(
            "Enable dynamic normalize and limiter audio filter. "
            "When enabled, audio uses dynaudnorm followed by alimiter to reduce clipping at high volume boosts. "
            "Disable it to use raw output without this processing."
        )

    def _help_mono_filter(self):
        return _(
            "Play audio as Mono. "
            "When enabled, a mono downmix filter is applied so left and right channels are combined. "
            "Disable it to keep the original channel layout."
        )
