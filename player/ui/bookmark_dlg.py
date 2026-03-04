import wx
from gettext import gettext as _

from helpers.utils import format_time


ID_MARK_JUMP = wx.ID_OK
ID_MARK_EDIT = wx.ID_EDIT
ID_MARK_DELETE = wx.ID_DELETE


class MarkManageDlg(wx.Dialog):
    def __init__(self, parent, marks):
        super().__init__(
            parent,
            title=_("Manage bookmarks"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._marks = []
        self._list = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN,
        )
        self._list.InsertColumn(0, _("Name"), width=260)
        self._list.InsertColumn(1, _("Position"), width=120)

        self._jump_btn = wx.Button(self, ID_MARK_JUMP, _("Jump"))
        self._edit_btn = wx.Button(self, ID_MARK_EDIT, _("Edit"))
        self._del_btn = wx.Button(self, ID_MARK_DELETE, _("Delete"))
        self._close_btn = wx.Button(self, wx.ID_CANCEL, _("Close"))
        self._jump_btn.SetDefault()

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self._jump_btn, 0, wx.RIGHT, 6)
        btn_sizer.Add(self._edit_btn, 0, wx.RIGHT, 6)
        btn_sizer.Add(self._del_btn, 0)
        btn_sizer.AddStretchSpacer(1)
        btn_sizer.Add(self._close_btn, 0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._list, 1, wx.ALL | wx.EXPAND, 8)
        sizer.Add(btn_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        self.SetSizerAndFit(sizer)
        self.SetMinSize((500, 320))
        self.CentreOnParent()

        self._list.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_select)
        self._list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_select)
        self._list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_activate)
        self._jump_btn.Bind(wx.EVT_BUTTON, self._on_jump)
        self._edit_btn.Bind(wx.EVT_BUTTON, self._on_edit)
        self._del_btn.Bind(wx.EVT_BUTTON, self._on_delete)

        self.set_marks(marks)

    def set_marks(self, marks, selected_id=""):
        self._marks = list(marks or [])
        self._list.DeleteAllItems()
        selected_index = -1
        selected_text = str(selected_id or "").strip()
        for idx, mark in enumerate(self._marks):
            row = self._list.InsertItem(idx, str(mark.name or ""))
            stamp = format_time(mark.pos)
            self._list.SetItem(row, 1, stamp or "00:00:00")
            if selected_text and str(mark.id or "") == selected_text:
                selected_index = idx
        if selected_index < 0 and self._marks:
            selected_index = 0
        if selected_index >= 0:
            self._list.Select(selected_index)
            self._list.Focus(selected_index)
        self._sync_buttons()

    def selected_id(self):
        idx = self._list.GetFirstSelected()
        if idx < 0 or idx >= len(self._marks):
            return ""
        return str(self._marks[idx].id or "")

    def _on_select(self, _event):
        self._sync_buttons()

    def _on_activate(self, _event):
        if self.selected_id():
            self.EndModal(ID_MARK_JUMP)

    def _on_jump(self, _event):
        if self.selected_id():
            self.EndModal(ID_MARK_JUMP)

    def _on_edit(self, _event):
        if self.selected_id():
            self.EndModal(ID_MARK_EDIT)

    def _on_delete(self, _event):
        if self.selected_id():
            self.EndModal(ID_MARK_DELETE)

    def _sync_buttons(self):
        ok = bool(self.selected_id())
        self._jump_btn.Enable(ok)
        self._edit_btn.Enable(ok)
        self._del_btn.Enable(ok)
