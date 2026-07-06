from gettext import gettext as _

from ui import dialogs
from .components import add_to_path
from .download import dl_audio_m4a
from .resolver import fetch_item
from .state import cur_url, is_yt
from .task_ui import run_task
from .ui_utils import copy_text, fmt_dl, pick_dir


def has_video(ctx):
    return is_yt(cur_url(ctx))


def dl_now(ctx):
    data = _cur_meta(ctx, need_desc=False)
    if data is None:
        ctx.speak(_("No YouTube video is active."), _("No YouTube video."))
        return
    dl_url(ctx, data["url"])


def show_desc(ctx):
    data = _cur_meta(ctx, need_desc=True)
    if data is None:
        ctx.speak(_("No YouTube video is active."), _("No YouTube video."))
        return
    title = str(data.get("title") or "").strip()
    desc = str(data.get("desc") or "").strip()
    if not desc:
        desc = _("No description is available.")
    text = f"{title}\n\n{desc}" if title else desc
    dlg = dialogs.TextInfoDialog(ctx.frame, _("Video description"), text)
    dlg.ShowModal()
    dlg.Destroy()


def copy_link(ctx):
    url = cur_url(ctx)
    if not is_yt(url):
        ctx.speak(_("No YouTube video is active."), _("No YouTube video."))
        return
    if copy_text(url):
        ctx.speak(_("Link copied."), _("Copied."))
    else:
        ctx.speak(_("Could not copy link."), _("Copy failed."))


def dl_url(ctx, url):
    if ctx.frame is None:
        return
    folder = pick_dir(ctx.frame)
    if not folder:
        return

    def job(cancel, _on_line, on_up):
        dl_audio_m4a(url, folder, cancel, on_update=on_up)
        return True

    out = run_task(
        ctx.frame,
        _("Downloading audio"),
        job,
        fmt_up=fmt_dl,
    )
    if out.can:
        return
    if not out.ok:
        err = out.err or _("Download failed.")
        ctx.speak(err, err)
        return
    ctx.speak(_("Download completed."), _("Download completed."))


def _load_item(ctx, url):
    add_to_path()

    def job(cancel, on_line, _on_up):
        return fetch_item(url, cancel, on_line=on_line)

    out = run_task(
        ctx.frame,
        _("Loading video details"),
        job,
        simple=True,
    )
    if out.can or not out.ok:
        return None
    return out.val


def _cur_meta(ctx, need_desc):
    url = cur_url(ctx)
    if not is_yt(url):
        return None
    fallback_title = str(ctx.player.current_title or "").strip()
    now = getattr(ctx, "yt_now", None)
    if isinstance(now, dict) and str(now.get("url") or "").strip() == url:
        title = str(now.get("title") or "").strip() or fallback_title
        desc = str(now.get("desc") or "").strip()
    else:
        title = fallback_title
        desc = ""
    if need_desc and not desc:
        item = _load_item(ctx, url)
        if item is not None:
            title = str(item.title or "").strip() or title
            desc = str(item.description or "").strip()
            ctx.yt_now = {"url": url, "title": title, "desc": desc}
    return {"url": url, "title": title, "desc": desc}
