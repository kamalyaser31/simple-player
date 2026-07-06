import wx
from gettext import gettext as _


class SoundCardDialog(wx.Dialog):
    def __init__(self, parent, device_labels, selection_index=0):
        super().__init__(
            parent,
            title=_("Sound Cards"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        label = wx.StaticText(self, label=_("Select sound card"))
        self._combo = wx.ComboBox(
            self,
            choices=device_labels,
            style=wx.CB_READONLY,
        )
        if device_labels:
            self._combo.SetSelection(max(0, min(selection_index, len(device_labels) - 1)))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 0, wx.ALL, 8)
        sizer.Add(self._combo, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        if buttons:
            sizer.Add(buttons, 0, wx.ALL | wx.EXPAND, 8)
        self.SetSizerAndFit(sizer)
        self.SetMinSize((360, 180))
        self.CentreOnParent()

    def get_selection(self):
        return self._combo.GetSelection()
