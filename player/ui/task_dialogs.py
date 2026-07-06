import wx
from gettext import gettext as _


class TaskDialog(wx.Dialog):
    def __init__(self, parent, title, label=""):
        super().__init__(
            parent,
            title=title,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._label = wx.StaticText(self, label=label or "")
        self._text = wx.TextCtrl(
            self,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL,
        )
        self._prog = wx.Gauge(self, range=1000)
        self._cancel = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        self._cancelled = False

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(self._label, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 8)
        root.Add(self._text, 1, wx.ALL | wx.EXPAND, 8)
        root.Add(self._prog, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        root.Add(self._cancel, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_RIGHT, 8)
        self.SetSizerAndFit(root)
        self.SetMinSize((560, 320))
        self.CentreOnParent()

        self._cancel.Bind(wx.EVT_BUTTON, self._on_cancel)
        self.Bind(wx.EVT_CLOSE, self._on_close)

    def set_label(self, text):
        self._label.SetLabel(text or "")

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


class BusyDialog(wx.Dialog):
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

    def set_label(self, text):
        self._label.SetLabel(text or "")

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


# Compatibility aliases for existing code.
TaskDlg = TaskDialog
BusyDlg = BusyDialog
