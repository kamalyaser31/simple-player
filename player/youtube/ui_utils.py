import os
from gettext import gettext as _
from urllib.parse import parse_qs, urlparse

import wx


def link_kind(link):
    text = str(link or "").strip()
    low = text.lower()
    if "youtube.com/channel/" in low:
        return "channel"
    if "youtube.com/@" in low and "watch?" not in low and "playlist?" not in low:
        return "channel"
    if "youtube.com/playlist" in low:
        return "playlist"
    try:
        params = parse_qs(urlparse(text).query or "")
    except Exception:
        params = {}
    if "list" in params and bool(params.get("list")):
        return "playlist"
    return "video"


def ask_link(parent):
    dlg = wx.TextEntryDialog(
        parent,
        _("Enter a YouTube video or playlist link."),
        _("Open YouTube Link"),
    )
    try:
        if dlg.ShowModal() != wx.ID_OK:
            return ""
        return str(dlg.GetValue() or "").strip()
    finally:
        dlg.Destroy()


def ask_search(parent):
    dlg = wx.TextEntryDialog(
        parent,
        _("Enter search text."),
        _("Search YouTube"),
    )
    try:
        if dlg.ShowModal() != wx.ID_OK:
            return ""
        return str(dlg.GetValue() or "").strip()
    finally:
        dlg.Destroy()


def ask_video_or_playlist(parent):
    dlg = wx.Dialog(
        parent,
        title=_("Open YouTube Link"),
        style=wx.DEFAULT_DIALOG_STYLE,
    )
    message = wx.StaticText(
        dlg,
        label=_(
            "The app detected that this YouTube link contains a playlist and a video ID. "
            "Choose how you want to proceed."
        ),
    )
    video_btn = wx.Button(dlg, wx.ID_YES, _("Play the video"))
    playlist_btn = wx.Button(dlg, wx.ID_NO, _("Open the playlist"))
    cancel_btn = wx.Button(dlg, wx.ID_CANCEL, _("Cancel"))
    video_btn.SetDefault()
    dlg.SetEscapeId(wx.ID_CANCEL)
    video_btn.Bind(wx.EVT_BUTTON, lambda _e: dlg.EndModal(wx.ID_YES))
    playlist_btn.Bind(wx.EVT_BUTTON, lambda _e: dlg.EndModal(wx.ID_NO))
    cancel_btn.Bind(wx.EVT_BUTTON, lambda _e: dlg.EndModal(wx.ID_CANCEL))

    button_sizer = wx.BoxSizer(wx.HORIZONTAL)
    button_sizer.Add(video_btn, 0, wx.RIGHT, 6)
    button_sizer.Add(playlist_btn, 0, wx.RIGHT, 6)
    button_sizer.Add(cancel_btn, 0)

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(message, 0, wx.ALL | wx.EXPAND, 10)
    sizer.Add(button_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_RIGHT, 10)
    dlg.SetSizerAndFit(sizer)
    dlg.CentreOnParent()
    try:
        code = dlg.ShowModal()
        if code == wx.ID_YES:
            return "video"
        if code == wx.ID_NO:
            return "playlist"
        return ""
    finally:
        dlg.Destroy()


def copy_text(text):
    clip = wx.Clipboard.Get()
    if not clip.Open():
        return False
    try:
        data = wx.TextDataObject()
        data.SetText(str(text or ""))
        clip.SetData(data)
        clip.Flush()
        return True
    finally:
        clip.Close()


def open_url(url):
    target = str(url or "").strip()
    if not target:
        return False
    try:
        if wx.LaunchDefaultBrowser(target):
            return True
    except Exception:
        pass
    try:
        os.startfile(target)
        return True
    except Exception:
        return False


def pick_dir(parent):
    dlg = wx.DirDialog(
        parent,
        _("Select download folder"),
        style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
    )
    try:
        if dlg.ShowModal() != wx.ID_OK:
            return ""
        return str(dlg.GetPath() or "")
    finally:
        dlg.Destroy()


def fmt_dl(data):
    pct = float(data.get("pct", 0.0))
    total_text = str(data.get("total_text") or "").strip()
    total = total_text or fmt_bytes(data.get("total_b", 0))
    got = fmt_bytes(data.get("got_b", 0))
    return _(
        "Total size: {total}\nDownloaded: {got}\nPercentage: {pct:.2f}%"
    ).format(
        total=total,
        got=got,
        pct=pct,
    )


def fmt_bytes(value):
    try:
        num = int(value)
    except Exception:
        num = 0
    if num <= 0:
        return _("Unknown")
    size = float(num)
    units = ("B", "KB", "MB", "GB", "TB")
    idx = 0
    while size >= 1024.0 and idx < len(units) - 1:
        size /= 1024.0
        idx += 1
    if idx == 0:
        return f"{int(size)} {units[idx]}"
    return f"{size:.2f} {units[idx]}"


def res_label(ses):
    kind = str(ses.get("kind") or "").strip().lower()
    if kind == "search":
        return _("Search results")
    if kind == "playlist":
        return _("Playlist videos")
    return _("Videos")
