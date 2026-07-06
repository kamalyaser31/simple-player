import wx
from gettext import gettext as _


class RecordingSettingsPanel(wx.Panel):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self._settings = settings
        self._help_map = {}

        self._channels_label = wx.StaticText(self, label=_("Channels"))
        self._channels_values = ["mono", "stereo"]
        self._channels_labels = [_("Mono"), _("Stereo")]
        self._channels_choice = wx.Choice(self, choices=self._channels_labels)
        self._set_channels(self._settings.get_rec_channels())

        self._quality_label = wx.StaticText(self, label=_("Audio quality (kbps)"))
        self._quality_values = [32, 64, 92, 128, 160, 192, 320]
        self._quality_labels = [f"{value}kbps" for value in self._quality_values]
        self._quality_choice = wx.Choice(self, choices=self._quality_labels)
        self._set_quality(self._settings.get_rec_quality())

        self._format_label = wx.StaticText(self, label=_("Audio format"))
        self._format_values = ["wav", "mp3"]
        self._format_labels = ["WAV", "MP3"]
        self._format_choice = wx.Choice(self, choices=self._format_labels)
        self._set_format(self._settings.get_rec_format())

        self._folder_label = wx.StaticText(self, label=_("Recordings folder"))
        self._folder_text = wx.TextCtrl(self)
        self._folder_text.SetValue(self._settings.get_rec_folder())
        self._browse_btn = wx.Button(self, label=_("Browse..."))
        self._browse_btn.Bind(wx.EVT_BUTTON, self._on_browse)

        folder_row = wx.BoxSizer(wx.HORIZONTAL)
        folder_row.Add(self._folder_text, 1, wx.RIGHT | wx.EXPAND, 6)
        folder_row.Add(self._browse_btn, 0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        row = wx.BoxSizer(wx.VERTICAL)
        row.Add(self._channels_label, 0, wx.BOTTOM, 4)
        row.Add(self._channels_choice, 0, wx.EXPAND)
        sizer.Add(row, 0, wx.ALL | wx.EXPAND, 8)

        row = wx.BoxSizer(wx.VERTICAL)
        row.Add(self._quality_label, 0, wx.BOTTOM, 4)
        row.Add(self._quality_choice, 0, wx.EXPAND)
        sizer.Add(row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)

        row = wx.BoxSizer(wx.VERTICAL)
        row.Add(self._format_label, 0, wx.BOTTOM, 4)
        row.Add(self._format_choice, 0, wx.EXPAND)
        sizer.Add(row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)

        row = wx.BoxSizer(wx.VERTICAL)
        row.Add(self._folder_label, 0, wx.BOTTOM, 4)
        row.Add(folder_row, 0, wx.EXPAND)
        sizer.Add(row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        self.SetSizer(sizer)

        self._help_map[self._channels_choice] = self._help_channels
        self._help_map[self._quality_choice] = self._help_quality
        self._help_map[self._format_choice] = self._help_format
        self._help_map[self._folder_text] = self._help_folder
        self._help_map[self._browse_btn] = self._help_folder

    def apply(self):
        idx = self._channels_choice.GetSelection()
        if idx == wx.NOT_FOUND:
            idx = 1
        self._settings.set_rec_channels(self._channels_values[idx])

        qidx = self._quality_choice.GetSelection()
        if qidx == wx.NOT_FOUND:
            qidx = self._quality_values.index(192)
        self._settings.set_rec_quality(self._quality_values[qidx])

        fidx = self._format_choice.GetSelection()
        if fidx == wx.NOT_FOUND:
            fidx = 0
        self._settings.set_rec_format(self._format_values[fidx])

        self._settings.set_rec_folder(self._folder_text.GetValue().strip())

    def refresh_from_settings(self):
        self._set_channels(self._settings.get_rec_channels())
        self._set_quality(self._settings.get_rec_quality())
        self._set_format(self._settings.get_rec_format())
        self._folder_text.SetValue(self._settings.get_rec_folder())

    def get_context_help(self, focused):
        control = focused
        while control is not None:
            if control in self._help_map:
                return self._help_map[control]()
            if control is self:
                break
            control = control.GetParent()
        return _(
            "Recording settings page. Configure channels, bitrate, output format, and destination folder."
        )

    def _help_channels(self):
        return _("Recording channels. Choose Mono or Stereo.")

    def _help_quality(self):
        return _(
            "Recording bitrate in kilobits per second. "
            "Choose one of the preset values from 32 to 320. "
            "This mainly affects compressed formats such as MP3."
        )

    def _help_format(self):
        return _("Recording format. WAV is uncompressed. MP3 is compressed.")

    def _help_folder(self):
        return _("Recordings folder path. Use Browse to choose where new recordings are saved.")

    def _set_channels(self, value):
        try:
            idx = self._channels_values.index(str(value or "stereo").strip().lower())
        except ValueError:
            idx = 1
        self._channels_choice.SetSelection(idx)

    def _set_format(self, value):
        try:
            idx = self._format_values.index(str(value or "wav").strip().lower())
        except ValueError:
            idx = 0
        self._format_choice.SetSelection(idx)

    def _set_quality(self, value):
        try:
            q = int(value)
        except (TypeError, ValueError):
            q = 192
        try:
            idx = self._quality_values.index(q)
        except ValueError:
            idx = self._quality_values.index(192)
        self._quality_choice.SetSelection(idx)

    def _on_browse(self, _event):
        current = self._folder_text.GetValue().strip()
        with wx.DirDialog(
            self,
            message=_("Choose recordings folder"),
            defaultPath=current or "",
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self._folder_text.SetValue(dlg.GetPath())
