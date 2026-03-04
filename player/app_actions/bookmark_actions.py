import wx
from gettext import gettext as _

from helpers.utils import format_time
from ui.bookmark_dlg import ID_MARK_DELETE, ID_MARK_EDIT, ID_MARK_JUMP, MarkManageDlg


def add_mark(ctx):
    path, pos = _current(ctx)
    if not path:
        return
    parent = ctx.frame
    if parent is None:
        return
    default_name = _("Bookmark {time}").format(time=format_time(pos) or "00:00:00")
    dlg = wx.TextEntryDialog(parent, _("Enter bookmark name"), _("Add a new bookmark"), default_name)
    if dlg.ShowModal() == wx.ID_OK:
        name = str(dlg.GetValue() or "").strip()
        if not name:
            wx.MessageBox(
                _("Bookmark name cannot be empty."),
                _("Bookmarks"),
                wx.OK | wx.ICON_WARNING,
                parent=parent,
            )
            dlg.Destroy()
            return
        try:
            mark = ctx.marks.add(path, pos, name)
        except Exception as exc:
            wx.MessageBox(
                str(exc) or _("Could not add bookmark."),
                _("Bookmarks"),
                wx.OK | wx.ICON_ERROR,
                parent=parent,
            )
            dlg.Destroy()
            return
        stamp = format_time(mark.pos) or "00:00:00"
        wx.MessageBox(
            _("Bookmark '{name}' added at {time}.").format(name=mark.name, time=stamp),
            _("Success"),
            wx.OK | wx.ICON_INFORMATION,
            parent=parent,
        )
    dlg.Destroy()


def manage_marks(ctx):
    path, _pos = _current(ctx, require_position=False)
    if not path:
        return
    parent = ctx.frame
    if parent is None:
        return
    marks = ctx.marks.list_for(path)
    if not marks:
        wx.MessageBox(
            _("No bookmarks found for the current file."),
            _("Bookmarks"),
            wx.OK | wx.ICON_INFORMATION,
            parent=parent,
        )
        return

    dlg = MarkManageDlg(parent, marks)
    selected = ""
    while True:
        code = dlg.ShowModal()
        if code in (wx.ID_CANCEL, wx.ID_CLOSE):
            break
        selected = dlg.selected_id()
        if not selected:
            continue
        if code == ID_MARK_JUMP:
            mark = _find(ctx, path, selected)
            if mark is None:
                _refresh(dlg, ctx, path, selected)
                continue
            _jump(ctx, mark)
            break
        if code == ID_MARK_EDIT:
            mark = _find(ctx, path, selected)
            if mark is None:
                _refresh(dlg, ctx, path, selected)
                continue
            edit = wx.TextEntryDialog(
                parent,
                _("Edit bookmark name"),
                _("Manage bookmarks"),
                str(mark.name or ""),
            )
            if edit.ShowModal() == wx.ID_OK:
                new_name = str(edit.GetValue() or "").strip()
                if not new_name:
                    wx.MessageBox(
                        _("Bookmark name cannot be empty."),
                        _("Error"),
                        wx.OK | wx.ICON_WARNING,
                        parent=parent,
                    )
                else:
                    ctx.marks.rename(path, selected, new_name)
            edit.Destroy()
            _refresh(dlg, ctx, path, selected)
            continue
        if code == ID_MARK_DELETE:
            mark = _find(ctx, path, selected)
            if mark is None:
                _refresh(dlg, ctx, path, selected)
                continue
            confirm = wx.MessageBox(
                _("Delete bookmark '{name}'?").format(name=mark.name),
                _("Confirm delete"),
                wx.YES_NO | wx.ICON_WARNING,
                parent=parent,
            )
            if confirm == wx.YES:
                ctx.marks.delete(path, selected)
            marks = ctx.marks.list_for(path)
            if not marks:
                wx.MessageBox(
                    _("All bookmarks for this file were removed."),
                    _("Bookmarks"),
                    wx.OK | wx.ICON_INFORMATION,
                    parent=parent,
                )
                break
            dlg.set_marks(marks, selected_id="")
            continue
    dlg.Destroy()


def jump_mark_slot(ctx, slot):
    path, _pos = _current(ctx, require_position=False)
    if not path:
        return
    mark = ctx.marks.slot(path, slot)
    if mark is None:
        ctx.speak(
            _("No bookmark in slot {slot}.").format(slot=int(slot)),
            _("No bookmark {slot}.").format(slot=int(slot)),
        )
        return
    _jump(ctx, mark)


def _current(ctx, require_position=True):
    path = str(ctx.player.current_path or "").strip()
    if not path:
        ctx.speak(_("No file loaded."), _("No file."))
        return "", 0.0
    try:
        pos = float(ctx.player.get_elapsed() or 0.0)
    except (TypeError, ValueError):
        pos = 0.0
    if pos < 0:
        pos = 0.0
    if require_position and ctx.player.get_duration() is None:
        pos = 0.0
    return path, pos


def _find(ctx, path, mark_id):
    target = str(mark_id or "").strip()
    if not target:
        return None
    for mark in ctx.marks.list_for(path):
        if str(mark.id or "").strip() == target:
            return mark
    return None


def _refresh(dlg, ctx, path, selected):
    marks = ctx.marks.list_for(path)
    dlg.set_marks(marks, selected_id=selected)


def _jump(ctx, mark):
    ctx.player.seek_absolute(mark.pos)
    stamp = format_time(mark.pos) or "00:00:00"
    ctx.speak(
        _("Jumped to bookmark {name}.").format(name=mark.name),
        _("Jumped to '{name}' at {time}.").format(name=mark.name, time=stamp),
    )
