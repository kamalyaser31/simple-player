import wx
from gettext import gettext as _


class AppUpdateDialog(wx.Dialog):
    def __init__(self, parent, app_name, version, changes):
        super().__init__(
            parent,
            title=_("Application update"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        message = _(
            "A new version of {app_name} has been detected. Would you like to update?"
        ).format(app_name=app_name)
        info = wx.StaticText(self, label=message)
        info.Wrap(520)

        label = wx.StaticText(self, label=_("What's new"))
        text = wx.TextCtrl(
            self,
            value=str(changes or ""),
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL,
        )
        text.SetInsertionPoint(0)

        version_label = wx.StaticText(self, label=_("Version: {version}").format(version=version))

        yes = wx.Button(self, wx.ID_YES, _("Update"))
        no = wx.Button(self, wx.ID_NO, _("Later"))
        yes.SetDefault()

        btn = wx.BoxSizer(wx.HORIZONTAL)
        btn.AddStretchSpacer(1)
        btn.Add(yes, 0, wx.RIGHT, 8)
        btn.Add(no, 0)

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(info, 0, wx.ALL | wx.EXPAND, 10)
        root.Add(version_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        root.Add(label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        root.Add(text, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        root.Add(btn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizerAndFit(root)
        self.SetMinSize((620, 420))
        self.CentreOnParent()

        yes.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_YES))
        no.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_NO))
