import wx
from gettext import gettext as _


MISSING_MSG = _(
    "The app detected that some components for YouTube are missing. "
    "Would you like to download the required libraries? "
    "If you do not wish to use YouTube search features, you can ignore this message."
)


class MissingDlg(wx.Dialog):
    def __init__(self, parent):
        super().__init__(
            parent,
            title=_("YouTube Components"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        text = wx.StaticText(self, label=MISSING_MSG)
        text.Wrap(420)
        self._skip = wx.CheckBox(self, label=_("Don't show this message again"))
        yes = wx.Button(self, wx.ID_YES, _("Yes"))
        no = wx.Button(self, wx.ID_NO, _("No"))
        yes.SetDefault()

        btn = wx.BoxSizer(wx.HORIZONTAL)
        btn.AddStretchSpacer(1)
        btn.Add(yes, 0, wx.RIGHT, 8)
        btn.Add(no, 0)

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(text, 0, wx.ALL | wx.EXPAND, 10)
        root.Add(self._skip, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        root.Add(btn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizerAndFit(root)
        self.SetMinSize((500, 220))
        self.CentreOnParent()

        yes.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_YES))
        no.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_NO))

    def skip_next(self):
        return self._skip.GetValue()


class TaskDlg(wx.Dialog):
    def __init__(self, parent, title):
        super().__init__(
            parent,
            title=title,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._text = wx.TextCtrl(
            self,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL,
        )
        self._prog = wx.Gauge(self, range=1000)
        self._cancel = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        self._cancelled = False

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(self._text, 1, wx.ALL | wx.EXPAND, 8)
        root.Add(self._prog, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        root.Add(self._cancel, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_RIGHT, 8)
        self.SetSizerAndFit(root)
        self.SetMinSize((560, 320))
        self.CentreOnParent()

        self._cancel.Bind(wx.EVT_BUTTON, self._on_cancel)
        self.Bind(wx.EVT_CLOSE, self._on_close)

    def set_text(self, text):
        self._text.SetValue(text or "")
        self._text.SetInsertionPointEnd()

    def append(self, line):
        old = self._text.GetValue()
        if old:
            self._text.SetValue(old + "\n" + line)
        else:
            self._text.SetValue(line)
        self._text.SetInsertionPointEnd()

    def set_progress(self, pct):
        try:
            value = float(pct)
        except Exception:
            value = 0.0
        if value < 0.0:
            value = 0.0
        if value > 100.0:
            value = 100.0
        self._prog.SetValue(int(round(value * 10.0)))

    def was_cancelled(self):
        return self._cancelled

    def _on_cancel(self, _event):
        self._cancelled = True

    def _on_close(self, _event):
        self._cancelled = True


class BusyDlg(wx.Dialog):
    def __init__(self, parent, title, label=""):
        super().__init__(
            parent,
            title=title,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._label = wx.StaticText(self, label=label or "")
        self._prog = wx.Gauge(self, range=1000)
        self._cancel = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        self._cancelled = False

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(self._label, 0, wx.ALL | wx.EXPAND, 8)
        root.Add(self._prog, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        root.Add(self._cancel, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_RIGHT, 8)
        self.SetSizerAndFit(root)
        self.SetMinSize((420, 160))
        self.CentreOnParent()

        self._cancel.Bind(wx.EVT_BUTTON, self._on_cancel)
        self.Bind(wx.EVT_CLOSE, self._on_close)

    def pulse(self):
        self._prog.Pulse()

    def set_progress(self, pct):
        try:
            value = float(pct)
        except Exception:
            value = 0.0
        if value < 0.0:
            value = 0.0
        if value > 100.0:
            value = 100.0
        self._prog.SetValue(int(round(value * 10.0)))

    def was_cancelled(self):
        return self._cancelled

    def _on_cancel(self, _event):
        self._cancelled = True

    def _on_close(self, _event):
        self._cancelled = True


class ResultsDlg(wx.Dialog):
    def __init__(self, parent, title, label):
        super().__init__(
            parent,
            title=title,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._label = wx.StaticText(self, label=label or _("Videos"))
        self._list = wx.ListBox(self, choices=[])
        self._play = wx.Button(self, wx.ID_ANY, _("Play"))
        self._download = wx.Button(self, wx.ID_ANY, _("Download"))
        self._close = wx.Button(self, wx.ID_CANCEL, _("Close"))

        btn = wx.BoxSizer(wx.HORIZONTAL)
        btn.Add(self._play, 0, wx.RIGHT, 6)
        btn.Add(self._download, 0, wx.RIGHT, 6)
        btn.AddStretchSpacer(1)
        btn.Add(self._close, 0)

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(self._label, 0, wx.ALL | wx.EXPAND, 8)
        root.Add(self._list, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        root.Add(btn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        self.SetSizerAndFit(root)
        self.SetMinSize((600, 380))
        self.CentreOnParent()

        self._id_copy = wx.NewIdRef()
        self._id_browser = wx.NewIdRef()
        self._id_channel = wx.NewIdRef()
        self._id_dl = wx.NewIdRef()
        self._id_play = wx.NewIdRef()
        self._build_accels()
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

    def set_label(self, text):
        self._label.SetLabel(text or "")

    def set_items(self, labels):
        self._list.Set(list(labels or []))
        if self._list.GetCount() > 0:
            self._list.SetSelection(0)

    def append_items(self, labels):
        for label in list(labels or []):
            self._list.Append(label)

    def get_selection(self):
        return self._list.GetSelection()

    @property
    def list_box(self):
        return self._list

    @property
    def play_btn(self):
        return self._play

    @property
    def download_btn(self):
        return self._download

    @property
    def close_btn(self):
        return self._close

    @property
    def id_copy(self):
        return int(self._id_copy)

    @property
    def id_browser(self):
        return int(self._id_browser)

    @property
    def id_channel(self):
        return int(self._id_channel)

    @property
    def id_dl(self):
        return int(self._id_dl)

    @property
    def id_play(self):
        return int(self._id_play)

    def show_menu(self):
        menu = wx.Menu()
        menu.Append(self.id_copy, _("Copy link\tCtrl+C"))
        menu.Append(self.id_browser, _("Open in browser\tCtrl+B"))
        menu.Append(self.id_channel, _("Navigate to channel\tCtrl+N"))
        menu.AppendSeparator()
        menu.Append(self.id_dl, _("Download"))
        self.PopupMenu(menu)
        menu.Destroy()

    def _build_accels(self):
        entries = []
        for flags, key, cmd in (
            (wx.ACCEL_NORMAL, wx.WXK_RETURN, self.id_play),
            (wx.ACCEL_NORMAL, wx.WXK_NUMPAD_ENTER, self.id_play),
            (wx.ACCEL_CTRL, ord("C"), self.id_copy),
            (wx.ACCEL_CTRL, ord("B"), self.id_browser),
            (wx.ACCEL_CTRL, ord("N"), self.id_channel),
        ):
            entry = wx.AcceleratorEntry()
            entry.Set(flags, key, cmd)
            entries.append(entry)
        self.SetAcceleratorTable(wx.AcceleratorTable(entries))

    def _on_char_hook(self, event):
        key = event.GetKeyCode()
        if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            cmd = wx.CommandEvent(wx.EVT_MENU.typeId, self.id_play)
            wx.PostEvent(self, cmd)
            return
        event.Skip()


class PlaylistDlg(ResultsDlg):
    pass
