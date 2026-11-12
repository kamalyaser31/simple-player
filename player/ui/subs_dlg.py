import wx
from gettext import gettext as _

ID_SUB_OPEN = wx.ID_OPEN
ID_SUB_ADD = wx.ID_ADD
ID_SUB_REMOVE = wx.ID_DELETE


def sub_label(sub):
    if str(sub.kind or "") == "playlist":
        return _("{name} - playlist").format(name=sub.name)
    return _("{name} - channel").format(name=sub.name)


class SubsDlg(wx.Dialog):
    def __init__(self, parent, subs):
        super().__init__(
            parent,
            title=_("YouTube subscriptions"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._items = []
        # The label must directly precede the list so screen readers name it.
        self._label = wx.StaticText(self, label=_("Subscriptions"))
        self._list = wx.ListBox(self, choices=[], style=wx.LB_SINGLE)

        self._open_btn = wx.Button(self, ID_SUB_OPEN, _("Open"))
        self._add_btn = wx.Button(self, ID_SUB_ADD, _("Add by link..."))
        self._remove_btn = wx.Button(self, ID_SUB_REMOVE, _("Remove..."))
        self._close_btn = wx.Button(self, wx.ID_CANCEL, _("Close"))
        self._open_btn.SetDefault()

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self._open_btn, 0, wx.RIGHT, 6)
        btn_sizer.Add(self._add_btn, 0, wx.RIGHT, 6)
        btn_sizer.Add(self._remove_btn, 0)
        btn_sizer.AddStretchSpacer(1)
        btn_sizer.Add(self._close_btn, 0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._label, 0, wx.ALL | wx.EXPAND, 8)
        sizer.Add(self._list, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        sizer.Add(btn_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        self.SetSizerAndFit(sizer)
        self.SetMinSize((560, 340))
        self.CentreOnParent()

        self._list.Bind(wx.EVT_LISTBOX, self._on_select)
        self._list.Bind(wx.EVT_LISTBOX_DCLICK, self._on_open)
        self._list.Bind(wx.EVT_CHAR_HOOK, self._on_list_key)
        self._open_btn.Bind(wx.EVT_BUTTON, self._on_open)
        self._add_btn.Bind(wx.EVT_BUTTON, self._on_add)
        self._remove_btn.Bind(wx.EVT_BUTTON, self._on_remove)

        self.set_items(subs)

    def set_items(self, subs, selected_id=""):
        self._items = list(subs or [])
        self._list.Set([sub_label(sub) for sub in self._items])
        target = str(selected_id or "").strip()
        index = 0
        for idx, sub in enumerate(self._items):
            if target and str(sub.id or "") == target:
                index = idx
                break
        if self._items:
            self._list.SetSelection(index)
        self._sync_buttons()

    def selected_id(self):
        idx = self._list.GetSelection()
        if idx == wx.NOT_FOUND or idx >= len(self._items):
            return ""
        return str(self._items[idx].id or "")

    def _on_select(self, _event):
        self._sync_buttons()

    def _on_open(self, _event):
        if self.selected_id():
            self.EndModal(ID_SUB_OPEN)

    def _on_add(self, _event):
        self.EndModal(ID_SUB_ADD)

    def _on_remove(self, _event):
        if self.selected_id():
            self.EndModal(ID_SUB_REMOVE)

    def _on_list_key(self, event):
        key = event.GetKeyCode()
        if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self._on_open(event)
            return
        if key == wx.WXK_DELETE:
            self._on_remove(event)
            return
        event.Skip()

    def _sync_buttons(self):
        has_selection = bool(self.selected_id())
        self._open_btn.Enable(has_selection)
        self._remove_btn.Enable(has_selection)
