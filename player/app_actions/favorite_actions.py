import wx
from gettext import gettext as _

from helpers.file_helpers import is_http_url, set_ready
from ui.favorite_dlg import (
    ID_FAV_ADD,
    ID_FAV_EDIT,
    ID_FAV_REMOVE,
    FavEditDlg,
    FavManageDlg,
    type_label,
)
from youtube.actions import open_yt_link
from youtube.link_validator import parse_link
from youtube.state import clear_ses


def manage_favs(ctx):
    parent = ctx.frame
    if parent is None:
        return
    if getattr(ctx, "favs", None) is None:
        return

    dlg = FavManageDlg(parent, ctx.favs.list_all())
    selected = ""
    while True:
        code = dlg.ShowModal()
        if code in (wx.ID_CANCEL, wx.ID_CLOSE):
            break
        selected = dlg.selected_id()
        if code == ID_FAV_ADD:
            added_id = _add_item(parent, ctx)
            dlg.set_items(ctx.favs.list_all(), selected_id=added_id)
            continue
        if code == ID_FAV_EDIT:
            if not selected:
                continue
            _edit_item(parent, ctx, selected)
            dlg.set_items(ctx.favs.list_all(), selected_id=selected)
            continue
        if code == ID_FAV_REMOVE:
            if not selected:
                continue
            if _remove_item(parent, ctx, selected):
                selected = ""
            dlg.set_items(ctx.favs.list_all(), selected_id=selected)
            continue
        if code == wx.ID_OK:
            if not selected:
                continue
            item = ctx.favs.get(selected)
            if item is None:
                dlg.set_items(ctx.favs.list_all(), selected_id="")
                continue
            if _open_item(ctx, item):
                break
    dlg.Destroy()


def _add_item(parent, ctx):
    dlg = FavEditDlg(parent, _("Add favorite"))
    added_id = ""
    if dlg.ShowModal() == wx.ID_OK:
        data = dlg.get_data()
        err = _validate(data)
        if err:
            wx.MessageBox(err, _("Favorite videos"), wx.OK | wx.ICON_WARNING, parent=parent)
            dlg.Destroy()
            return ""
        try:
            item = ctx.favs.add(data["name"], data["kind"], data["link"])
        except Exception as exc:
            wx.MessageBox(
                str(exc) or _("Could not add favorite."),
                _("Favorite videos"),
                wx.OK | wx.ICON_ERROR,
                parent=parent,
            )
            dlg.Destroy()
            return ""
        added_id = str(item.id or "")
    dlg.Destroy()
    return added_id


def _edit_item(parent, ctx, fav_id):
    item = ctx.favs.get(fav_id)
    if item is None:
        return
    dlg = FavEditDlg(
        parent,
        _("Edit favorite"),
        name=item.name,
        kind=item.kind,
        link=item.link,
    )
    if dlg.ShowModal() == wx.ID_OK:
        data = dlg.get_data()
        err = _validate(data)
        if err:
            wx.MessageBox(err, _("Favorite videos"), wx.OK | wx.ICON_WARNING, parent=parent)
            dlg.Destroy()
            return
        try:
            ctx.favs.update(fav_id, data["name"], data["kind"], data["link"])
        except Exception as exc:
            wx.MessageBox(
                str(exc) or _("Could not update favorite."),
                _("Favorite videos"),
                wx.OK | wx.ICON_ERROR,
                parent=parent,
            )
    dlg.Destroy()


def _remove_item(parent, ctx, fav_id):
    item = ctx.favs.get(fav_id)
    if item is None:
        return False
    yes = wx.MessageBox(
        _("Remove favorite '{name}' ({kind})?").format(
            name=item.name,
            kind=type_label(item.kind),
        ),
        _("Confirm remove"),
        wx.YES_NO | wx.ICON_WARNING,
        parent=parent,
    )
    if yes != wx.YES:
        return False
    return bool(ctx.favs.delete(fav_id))


def _open_item(ctx, item):
    link = str(item.link or "").strip()
    kind = str(item.kind or "").strip().lower()
    if kind == "generic_stream":
        clear_ses(ctx)
        if ctx.player.open_stream(link, append=True):
            set_ready(ctx)
            return True
        wx.MessageBox(
            _("Could not open stream link."),
            _("Favorite videos"),
            wx.OK | wx.ICON_ERROR,
            parent=ctx.frame,
        )
        return False

    if kind in ("video", "playlist", "combined"):
        return bool(open_yt_link(ctx, link, forced_kind=kind))

    wx.MessageBox(
        _("Unsupported favorite type."),
        _("Favorite videos"),
        wx.OK | wx.ICON_ERROR,
        parent=ctx.frame,
    )
    return False


def _validate(data):
    name = str(data.get("name") or "").strip()
    kind = str(data.get("kind") or "").strip().lower()
    link = str(data.get("link") or "").strip()
    if not name:
        return _("Name is required.")
    if not link:
        return _("Link is required.")

    if kind == "generic_stream":
        if not is_http_url(link):
            return _("Generic stream link must start with http or https.")
        return ""

    info = parse_link(link)
    if not info.is_http:
        return _("The link must start with http or https.")
    if not info.is_youtube:
        return _("The link must be a valid YouTube link for this type.")
    if kind == "video" and not bool(info.has_video):
        return _("Video favorites require a YouTube video link.")
    if kind == "playlist" and not bool(info.has_playlist):
        return _("Playlist favorites require a YouTube playlist link.")
    if kind == "combined" and not (bool(info.has_video) and bool(info.has_playlist)):
        return _("Combined link favorites require a link containing both video and playlist.")
    return ""
