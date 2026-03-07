import wx
from gettext import gettext as _


ID_FAV_ADD = wx.ID_ADD
ID_FAV_EDIT = wx.ID_EDIT
ID_FAV_REMOVE = wx.ID_DELETE

TYPE_CHOICES = (
    ("video", _("Video")),
    ("playlist", _("Playlist")),
    ("combined", _("Combined link")),
    ("generic_stream", _("Generic stream")),
)


def type_label(kind):
    key = str(kind or "").strip().lower()
    for value, label in TYPE_CHOICES:
        if value == key:
            return label
    return key


class FavManageDlg(wx.Dialog):
    def __init__(self, parent, items):
        super().__init__(
            parent,
            title=_("Favorite videos"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._items = []
        self._list = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN,
        )
        self._list.InsertColumn(0, _("Name"), width=180)
        self._list.InsertColumn(1, _("Type"), width=140)
        self._list.InsertColumn(2, _("Link"), width=340)

        self._add_btn = wx.Button(self, ID_FAV_ADD, _("Add..."))
        self._edit_btn = wx.Button(self, ID_FAV_EDIT, _("Edit..."))
        self._remove_btn = wx.Button(self, ID_FAV_REMOVE, _("Remove..."))
        self._close_btn = wx.Button(self, wx.ID_CANCEL, _("Close"))

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self._add_btn, 0, wx.RIGHT, 6)
        btn_sizer.Add(self._edit_btn, 0, wx.RIGHT, 6)
        btn_sizer.Add(self._remove_btn, 0)
        btn_sizer.AddStretchSpacer(1)
        btn_sizer.Add(self._close_btn, 0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._list, 1, wx.ALL | wx.EXPAND, 8)
        sizer.Add(btn_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        self.SetSizerAndFit(sizer)
        self.SetMinSize((740, 360))
        self.CentreOnParent()

        self._list.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_select)
        self._list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_select)
        self._list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_activate)
        self._add_btn.Bind(wx.EVT_BUTTON, self._on_add)
        self._edit_btn.Bind(wx.EVT_BUTTON, self._on_edit)
        self._remove_btn.Bind(wx.EVT_BUTTON, self._on_remove)

        self.set_items(items)

    def set_items(self, items, selected_id=""):
        self._items = list(items or [])
        self._list.DeleteAllItems()
        selected_index = -1
        selected_text = str(selected_id or "").strip()
        for idx, item in enumerate(self._items):
            row = self._list.InsertItem(idx, str(item.name or ""))
            self._list.SetItem(row, 1, str(type_label(item.kind) or ""))
            self._list.SetItem(row, 2, str(item.link or ""))
            if selected_text and str(item.id or "") == selected_text:
                selected_index = idx
        if selected_index < 0 and self._items:
            selected_index = 0
        if selected_index >= 0:
            self._list.Select(selected_index)
            self._list.Focus(selected_index)
        self._sync_buttons()

    def selected_id(self):
        idx = self._list.GetFirstSelected()
        if idx < 0 or idx >= len(self._items):
            return ""
        return str(self._items[idx].id or "")

    def _on_select(self, _event):
        self._sync_buttons()

    def _on_activate(self, _event):
        if self.selected_id():
            self.EndModal(wx.ID_OK)

    def _on_add(self, _event):
        self.EndModal(ID_FAV_ADD)

    def _on_edit(self, _event):
        if self.selected_id():
            self.EndModal(ID_FAV_EDIT)

    def _on_remove(self, _event):
        if self.selected_id():
            self.EndModal(ID_FAV_REMOVE)

    def _sync_buttons(self):
        has_selection = bool(self.selected_id())
        self._edit_btn.Enable(has_selection)
        self._remove_btn.Enable(has_selection)


class FavEditDlg(wx.Dialog):
    def __init__(self, parent, title, name="", kind="video", link=""):
        super().__init__(
            parent,
            title=title,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._name_lbl = wx.StaticText(self, label=_("Name"))
        self._name_txt = wx.TextCtrl(self, value=str(name or ""))

        self._type_lbl = wx.StaticText(self, label=_("Type"))
        self._type_values = [row[0] for row in TYPE_CHOICES]
        self._type_labels = [row[1] for row in TYPE_CHOICES]
        self._type_choice = wx.Choice(self, choices=self._type_labels)

        self._link_lbl = wx.StaticText(self, label=_("Link"))
        self._link_txt = wx.TextCtrl(self, value=str(link or ""))
        self._set_kind(kind)

        form = wx.FlexGridSizer(0, 2, 8, 8)
        form.AddGrowableCol(1, 1)
        form.Add(self._name_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        form.Add(self._name_txt, 1, wx.EXPAND)
        form.Add(self._type_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        form.Add(self._type_choice, 1, wx.EXPAND)
        form.Add(self._link_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        form.Add(self._link_txt, 1, wx.EXPAND)

        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(form, 1, wx.ALL | wx.EXPAND, 10)
        if buttons is not None:
            sizer.Add(buttons, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizerAndFit(sizer)
        self.SetMinSize((560, 220))
        self.CentreOnParent()

    def get_data(self):
        idx = self._type_choice.GetSelection()
        if idx == wx.NOT_FOUND:
            idx = 0
        return {
            "name": str(self._name_txt.GetValue() or "").strip(),
            "kind": self._type_values[idx],
            "link": str(self._link_txt.GetValue() or "").strip(),
        }

    def _set_kind(self, kind):
        key = str(kind or "").strip().lower()
        try:
            idx = self._type_values.index(key)
        except ValueError:
            idx = 0
        self._type_choice.SetSelection(idx)
