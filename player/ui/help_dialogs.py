from gettext import gettext as _

import wx

try:
    import wx.adv as wxadv
except Exception:  # pragma: no cover - wx.adv is expected on desktop builds.
    wxadv = None


class AboutDialog(wx.Dialog):
    def __init__(self, parent, app_name, version, website):
        super().__init__(
            parent,
            title=_("About"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        about_text = _(
            "A lightweight, highly accessible media player designed for keyboard "
            "efficiency and seamless screen reader compatibility. Whether playing "
            "local audio files or streaming directly from YouTube, it offers "
            "precise control, advanced audio filtering, and a distraction-free "
            "experience.\n"
            "Developed by: Kamal yaser\n"
            "Version: {version}"
        ).format(version=version)

        desc = wx.TextCtrl(
            self,
            value=about_text,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP,
        )
        desc.SetInsertionPoint(0)
        desc.ShowPosition(0)

        title = wx.StaticText(self, label=app_name)
        font = title.GetFont()
        font.MakeBold()
        title.SetFont(font)

        if wxadv is not None:
            link = wxadv.HyperlinkCtrl(self, wx.ID_ANY, _("Visit website"), website)
        else:
            link = wx.StaticText(self, label=website)

        ok_btn = wx.Button(self, wx.ID_OK, _("OK"))
        ok_btn.SetDefault()
        ok_btn.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_OK))

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(title, 0, wx.ALL | wx.EXPAND, 10)
        root.Add(desc, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        root.Add(link, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        root.Add(ok_btn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_RIGHT, 10)
        self.SetSizerAndFit(root)
        self.SetMinSize((620, 380))
        self.CentreOnParent()
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

    def _on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
            return
        event.Skip()
