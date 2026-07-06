import wx
from gettext import gettext as _


AUDIO_WILDCARD = (
    "Audio Files (*.aac;*.aiff;*.alac;*.flac;*.m4a;*.mp3;*.mp4;*.ogg;*.opus;*.wav;*.wma)|"
    "*.aac;*.aiff;*.alac;*.flac;*.m4a;*.mp3;*.mp4;*.ogg;*.opus;*.wav;*.wma|"
    "All Files (*.*)|*.*"
)


def open_file_dialog(parent, initial_dir):
    with wx.FileDialog(
        parent,
        message="",
        defaultDir=initial_dir or "",
        wildcard=AUDIO_WILDCARD,
        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
    ) as dialog:
        if dialog.ShowModal() == wx.ID_OK:
            return dialog.GetPath(), dialog.GetDirectory()
    return None, None


def open_folder_dialog(parent, initial_dir):
    with wx.DirDialog(
        parent,
        message="",
        defaultPath=initial_dir or "",
        style=wx.DD_DIR_MUST_EXIST,
    ) as dialog:
        if dialog.ShowModal() == wx.ID_OK:
            return dialog.GetPath()
    return None


class GoToTimeDialog(wx.Dialog):
    def __init__(self, parent, duration_seconds, initial_seconds=0):
        super().__init__(
            parent,
            title=_("Go to time"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._total_seconds = _to_int_seconds(duration_seconds)
        self._selected_seconds = 0

        message = wx.StaticText(self, label=_("Choose time position:"))

        self._hours_label = wx.StaticText(self, label=_("Hours"))
        self._hours_spin = wx.SpinCtrl(self, min=0, max=0)
        self._minutes_label = wx.StaticText(self, label=_("Minutes"))
        self._minutes_spin = wx.SpinCtrl(self, min=0, max=0)
        self._seconds_label = wx.StaticText(self, label=_("Seconds"))
        self._seconds_spin = wx.SpinCtrl(self, min=0, max=0)

        self._hours_enabled = self._total_seconds >= 3600
        self._minutes_enabled = self._total_seconds >= 60

        if not self._hours_enabled:
            self._hours_label.Hide()
            self._hours_spin.Hide()
        if not self._minutes_enabled:
            self._minutes_label.Hide()
            self._minutes_spin.Hide()

        self._hours_spin.Bind(wx.EVT_SPINCTRL, self._on_spin_changed)
        self._minutes_spin.Bind(wx.EVT_SPINCTRL, self._on_spin_changed)
        self._seconds_spin.Bind(wx.EVT_SPINCTRL, self._on_spin_changed)
        self._hours_spin.Bind(wx.EVT_TEXT, self._on_spin_changed)
        self._minutes_spin.Bind(wx.EVT_TEXT, self._on_spin_changed)
        self._seconds_spin.Bind(wx.EVT_TEXT, self._on_spin_changed)

        self._ok_button = wx.Button(self, wx.ID_OK, _("OK"))
        self._cancel_button = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        self._ok_button.SetDefault()
        self._ok_button.Bind(wx.EVT_BUTTON, self._on_ok)

        btns = wx.BoxSizer(wx.HORIZONTAL)
        btns.AddStretchSpacer(1)
        btns.Add(self._ok_button, 0, wx.RIGHT, 6)
        btns.Add(self._cancel_button, 0)

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(message, 0, wx.ALL | wx.EXPAND, 8)
        if self._hours_enabled:
            root.Add(self._hours_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
            root.Add(self._hours_spin, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        if self._minutes_enabled:
            root.Add(self._minutes_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
            root.Add(self._minutes_spin, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        root.Add(self._seconds_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        root.Add(self._seconds_spin, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        root.Add(btns, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        self.SetSizerAndFit(root)
        self.SetMinSize((320, 220))
        self.CentreOnParent()

        self._set_initial(initial_seconds)
        self._update_limits()

    def get_seconds(self):
        return int(self._selected_seconds)

    def _set_initial(self, seconds):
        total = max(0, min(self._total_seconds, _to_int_seconds(seconds)))
        hours = total // 3600
        remain = total - (hours * 3600)
        minutes = remain // 60
        secs = remain - (minutes * 60)
        self._hours_spin.SetValue(hours)
        self._minutes_spin.SetValue(minutes)
        self._seconds_spin.SetValue(secs)

    def _on_spin_changed(self, _event):
        self._update_limits()

    def _update_limits(self):
        max_h = self._total_seconds // 3600 if self._hours_enabled else 0
        self._hours_spin.SetRange(0, max_h)
        if not self._hours_enabled:
            self._hours_spin.SetValue(0)
        h = self._clamp_value(self._hours_spin, 0, max_h)

        if self._minutes_enabled:
            if self._hours_enabled and h == max_h:
                max_m = min(59, max(0, (self._total_seconds - (h * 3600)) // 60))
            elif self._hours_enabled:
                max_m = 59
            else:
                max_m = max(0, self._total_seconds // 60)
            self._minutes_spin.SetRange(0, max_m)
            m = self._clamp_value(self._minutes_spin, 0, max_m)
        else:
            max_m = 0
            self._minutes_spin.SetRange(0, 0)
            self._minutes_spin.SetValue(0)
            m = 0

        remain = max(0, self._total_seconds - (h * 3600) - (m * 60))
        if self._minutes_enabled:
            max_s = 59 if remain >= 59 else remain
        else:
            max_s = remain
        self._seconds_spin.SetRange(0, max_s)
        self._clamp_value(self._seconds_spin, 0, max_s)

    def _clamp_value(self, control, low, high):
        try:
            value = int(control.GetValue())
        except Exception:
            value = low
        value = max(int(low), min(int(high), value))
        control.SetValue(value)
        return value

    def _on_ok(self, _event):
        try:
            h = int(self._hours_spin.GetValue()) if self._hours_enabled else 0
            m = int(self._minutes_spin.GetValue()) if self._minutes_enabled else 0
            s = int(self._seconds_spin.GetValue())
        except Exception:
            wx.MessageBox(
                _("Please enter a valid time value."),
                _("Go to time"),
                wx.OK | wx.ICON_ERROR,
                parent=self,
            )
            return

        target = (h * 3600) + (m * 60) + s
        if target < 0 or target > self._total_seconds:
            wx.MessageBox(
                _("The selected time exceeds the file duration."),
                _("Go to time"),
                wx.OK | wx.ICON_ERROR,
                parent=self,
            )
            return
        self._selected_seconds = target
        self.EndModal(wx.ID_OK)


class OpenedFilesDialog(wx.Dialog):
    def __init__(self, parent, entries, current_index=-1):
        super().__init__(
            parent,
            title=_("Opened Files"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._entries = list(entries or [])
        self._list = wx.ListBox(self, choices=self._entries)
        if 0 <= current_index < len(self._entries):
            self._list.SetSelection(current_index)

        message = wx.StaticText(self, label=_("Select file to jump to."))
        self._info_button = wx.Button(self, wx.ID_ANY, _("Playlist info"))
        self._jump_button = wx.Button(self, wx.ID_OK, _("Jump to selected"))
        self._cancel_button = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        self._jump_button.SetDefault()

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self._info_button, 0, wx.RIGHT, 6)
        button_sizer.AddStretchSpacer(1)
        button_sizer.Add(self._jump_button, 0, wx.RIGHT, 6)
        button_sizer.Add(self._cancel_button, 0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(message, 0, wx.ALL, 8)
        sizer.Add(self._list, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        sizer.Add(button_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        self.SetSizerAndFit(sizer)
        self.SetMinSize((420, 260))
        self.CentreOnParent()

        self._list.Bind(wx.EVT_LISTBOX_DCLICK, self._on_double_click)

    @property
    def info_button(self):
        return self._info_button

    def get_selection(self):
        return self._list.GetSelection()

    def _on_double_click(self, _event):
        if self.get_selection() != wx.NOT_FOUND:
            self.EndModal(wx.ID_OK)


class TextInfoDialog(wx.Dialog):
    def __init__(self, parent, title, info_text, close_label=None):
        super().__init__(
            parent,
            title=title or _("Information"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._text_box = wx.TextCtrl(
            self,
            value=info_text or "",
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP,
        )
        self._text_box.SetInsertionPoint(0)
        self._text_box.ShowPosition(0)

        close_button = wx.Button(self, wx.ID_CLOSE, close_label or _("Close"))
        close_button.Bind(wx.EVT_BUTTON, self._on_close)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._text_box, 1, wx.ALL | wx.EXPAND, 8)
        sizer.Add(close_button, 0, wx.ALL | wx.ALIGN_RIGHT, 8)
        self.SetSizerAndFit(sizer)
        self.SetMinSize((500, 320))
        self.CentreOnParent()
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

    def _on_close(self, _event):
        self.EndModal(wx.ID_CLOSE)

    def _on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
            return
        event.Skip()


class PlaylistInfoDialog(TextInfoDialog):
    def __init__(self, parent, info_text):
        super().__init__(parent, _("Playlist Info"), info_text, close_label=_("Close"))


def _to_int_seconds(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        try:
            number = int(float(value))
        except (TypeError, ValueError):
            number = 0
    if number < 0:
        return 0
    return int(number)
