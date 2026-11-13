import concurrent.futures
import http.client

import wx
from gettext import gettext as _

from subscriptions.feed import fetch_feed, merge_latest, parse_link, resolve_link
from ui.subs_dlg import ID_SUB_ADD, ID_SUB_OPEN, ID_SUB_REMOVE, SubsDlg
from youtube.actions import open_yt_link
from youtube.components import CancelledError
from youtube.flow import show_videos
from youtube.task_ui import run_task

FEED_WORKERS = 8
LATEST_LIMIT = 50


def open_latest(ctx):
    if ctx.frame is None or getattr(ctx, "subs", None) is None:
        return
    channels = ctx.subs.channels()
    if not channels:
        ctx.speak(_("You do not follow any channel yet."))
        manage_subs(ctx)
        return

    def work(cancel):
        feeds = []
        failed = 0
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=FEED_WORKERS)
        try:
            futures = [pool.submit(fetch_feed, "channel", sub.id) for sub in channels]
            for future in futures:
                while not future.done():
                    if cancel.is_set():
                        raise CancelledError()
                    concurrent.futures.wait([future], timeout=0.2)
                try:
                    feeds.append(future.result()[1])
                except Exception:
                    failed += 1
        finally:
            pool.shutdown(wait=False, cancel_futures=True)
        return feeds, failed

    out = _run(ctx, _("Loading subscriptions"), work)
    if out is None:
        return
    feeds, failed = out.val
    items = merge_latest(feeds, LATEST_LIMIT)
    if failed:
        ctx.speak(_("{n} channels could not be loaded.").format(n=failed))
        if not items:
            return
    show_videos(ctx, "feed", _("Latest subscription videos"), items)


def manage_subs(ctx):
    parent = ctx.frame
    if parent is None or getattr(ctx, "subs", None) is None:
        return

    dlg = SubsDlg(parent, ctx.subs.list_all())
    try:
        while True:
            code = dlg.ShowModal()
            if code in (wx.ID_CANCEL, wx.ID_CLOSE):
                break
            selected = dlg.selected_id()
            if code == ID_SUB_ADD:
                added_id = _add_by_link(ctx)
                dlg.set_items(ctx.subs.list_all(), selected_id=added_id)
                continue
            if code == ID_SUB_REMOVE:
                if selected and _remove_sub(ctx, selected):
                    selected = ""
                dlg.set_items(ctx.subs.list_all(), selected_id=selected)
                continue
            if code == ID_SUB_OPEN:
                sub = _find_sub(ctx, selected)
                if sub is None:
                    dlg.set_items(ctx.subs.list_all())
                    continue
                if _open_sub(ctx, sub):
                    break
    finally:
        dlg.Destroy()


def subscribe_channel(ctx, channel_url, channel_name):
    """Subscribe to a channel by its link; return True when newly added."""
    if ctx.frame is None or getattr(ctx, "subs", None) is None:
        return False
    return bool(_subscribe(ctx, channel_url, channel_name)[0])


def _add_by_link(ctx):
    dlg = wx.TextEntryDialog(
        ctx.frame, _("Channel or playlist link:"), _("Add subscription")
    )
    try:
        if dlg.ShowModal() != wx.ID_OK:
            return ""
        link = str(dlg.GetValue() or "").strip()
    finally:
        dlg.Destroy()
    if not link:
        return ""
    return _subscribe(ctx, link, "")[1]


def _subscribe(ctx, link, fallback_name):
    """Resolve a link and store it; return (added, sub_id)."""
    kind, ident = parse_link(link)
    known = _known_name(ctx, kind, ident)
    if known is not None:
        _speak_already(ctx, known)
        return False, ident

    out = _run(ctx, _("Adding subscription"), lambda _cancel: resolve_link(link))
    if out is None:
        return False, ""
    kind, ident, name = out.val
    name = name or fallback_name
    try:
        sub = ctx.subs.add(kind, ident, name)
    except Exception as exc:
        _show_error(ctx, str(exc) or _("Could not add subscription."))
        return False, ""
    if sub is None:
        _speak_already(ctx, name)
        return False, ident
    ctx.speak(_("Subscribed to {name}.").format(name=sub.name))
    return True, ident


def _known_name(ctx, kind, ident):
    """Name of an existing subscription found without network, or None."""
    if kind not in ("channel", "playlist"):
        return None
    for sub in ctx.subs.list_all():
        if sub.kind == kind and sub.id == ident:
            return sub.name
    return None


def _speak_already(ctx, name):
    ctx.speak(_("Already subscribed to {name}.").format(name=name))


def _find_sub(ctx, sub_id):
    for sub in ctx.subs.list_all():
        if sub.id == sub_id:
            return sub
    return None


def _remove_sub(ctx, sub_id):
    sub = _find_sub(ctx, sub_id)
    if sub is None:
        return False
    yes = wx.MessageBox(
        _("Remove {name} from subscriptions?").format(name=sub.name),
        _("Confirm remove"),
        wx.YES_NO | wx.ICON_WARNING,
        parent=ctx.frame,
    )
    if yes != wx.YES:
        return False
    return bool(ctx.subs.delete(sub_id))


def _open_sub(ctx, sub):
    if sub.kind == "playlist":
        return bool(open_yt_link(ctx, sub.url, forced_kind="playlist"))
    out = _run(ctx, _("Loading channel"), lambda _cancel: fetch_feed("channel", sub.id))
    if out is None:
        return False
    items = out.val[1]
    show_videos(ctx, "channel", sub.name, items)
    return True


def _run(ctx, title, work):
    """Run work(cancel) in the background; return the task output or None."""

    def job(cancel, _on_line, _on_up):
        try:
            return work(cancel)
        except (OSError, http.client.HTTPException):
            raise ValueError(
                _("Could not reach YouTube. Check your internet connection.")
            ) from None

    out = run_task(ctx.frame, title, job, simple=True)
    if out.can:
        return None
    if not out.ok:
        _show_error(ctx, out.err or _("Could not load YouTube data."))
        return None
    return out


def _show_error(ctx, message):
    wx.MessageBox(
        message,
        _("YouTube subscriptions"),
        wx.OK | wx.ICON_ERROR,
        parent=ctx.frame,
    )
