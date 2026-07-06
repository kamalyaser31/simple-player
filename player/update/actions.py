import concurrent.futures
import os
import queue
import subprocess

import wx
from gettext import gettext as _

from config.constants import APP_NAME, APP_VERSION
from ui.task_dialogs import BusyDialog, TaskDialog
from ui.update_dialogs import AppUpdateDialog
from update import service
from youtube import components as yt_components

_BG_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=1)


def check_updates_on_startup(ctx):
    if ctx.frame is None:
        return True
    if ctx.settings.get_check_app_updates():
        _check_updates_bg(ctx)
    if ctx.settings.get_check_yt_updates_startup():
        _check_yt_updates_bg(ctx)
    return True


def check_app_updates_now(ctx):
    if ctx.frame is None:
        return
    _check_app_updates(ctx, show_latest=True, silent_errors=False)


def update_youtube_components_now(ctx):
    if ctx.frame is None:
        return

    channel = ctx.settings.get_yt_dlp_channel()
    ctx.speak(_("Updating yt-dlp..."), _("Updating yt-dlp..."))

    def job(cancel, on_line, on_up):
        return yt_components.update_all(
            cancel,
            on_up,
            channel=channel,
            on_line=on_line,
        )

    out = _run_busy(
        ctx.frame,
        _("Updating yt-dlp"),
        job,
        on_line_ui=lambda line: ctx.speak(line, line),
    )
    if out["cancelled"]:
        ctx.speak(_("yt-dlp update cancelled."), _("Update cancelled."))
        return
    if not out["ok"]:
        err = out["error"] or _("Could not update yt-dlp.")
        wx.MessageBox(err, _("yt-dlp update"), wx.OK | wx.ICON_ERROR, parent=ctx.frame)
        return
    yt_components.add_to_path()
    info = out["value"] if isinstance(out["value"], dict) else {}
    old_ver = str(info.get("old_version", "") or "")
    new_ver = str(info.get("new_version", "") or "")
    used_channel = str(info.get("channel", "") or channel or "")
    updated = bool(info.get("updated"))
    if updated:
        msg = _("yt-dlp updated from {old} to {new} on '{ch}' channel.").format(
            old=old_ver or _("unknown"),
            new=new_ver or _("unknown"),
            ch=used_channel or "stable",
        )
    else:
        msg = _("yt-dlp is already up to date ({ver}) on '{ch}' channel.").format(
            ver=(new_ver or old_ver or _("unknown")),
            ch=used_channel or "stable",
        )
    wx.MessageBox(msg, _("yt-dlp update"), wx.OK | wx.ICON_INFORMATION, parent=ctx.frame)
    ctx.speak(msg, msg)


def _check_app_updates(ctx, show_latest, silent_errors):
    info = _fetch_info(ctx.frame)
    if info is None:
        if not silent_errors:
            wx.MessageBox(
                _("Could not check for updates."),
                _("Error"),
                wx.OK | wx.ICON_ERROR,
                parent=ctx.frame,
            )
        return True
    return _process_update_info(ctx, info, show_latest=show_latest)


def _process_update_info(ctx, info, show_latest):
    if ctx.frame is None:
        return True
    if not service.is_newer(info.version, APP_VERSION):
        if show_latest:
            wx.MessageBox(
                _("You are using the latest version."),
                _("Info"),
                wx.OK | wx.ICON_INFORMATION,
                parent=ctx.frame,
            )
        return True

    prompt = AppUpdateDialog(ctx.frame, APP_NAME, info.version, info.changes)
    try:
        if prompt.ShowModal() != wx.ID_YES:
            return True
    finally:
        prompt.Destroy()

    installer_mode = service.is_installer_mode()
    url = service.asset_url(info.version, installer_mode)
    dest = service.temp_download_path(info.version, installer_mode)

    def dl_job(cancel, _on_line, on_up):
        return service.download_file(url, dest, cancel, on_update=on_up)

    out = _run_task(
        ctx.frame,
        _("Downloading update"),
        dl_job,
        fmt_up=_fmt_update_status,
        label=_("Downloading update package..."),
    )
    if out["cancelled"]:
        return True
    if not out["ok"]:
        err = out["error"] or _("Could not download update.")
        wx.MessageBox(err, _("Error"), wx.OK | wx.ICON_ERROR, parent=ctx.frame)
        return True

    if not _launch_updater(dest):
        wx.MessageBox(
            _("Could not start the updater."),
            _("Error"),
            wx.OK | wx.ICON_ERROR,
            parent=ctx.frame,
        )
        return True

    wx.CallAfter(ctx.frame.Close)
    return False


def _check_updates_bg(ctx):
    frame = ctx.frame
    if frame is None:
        return

    def worker():
        try:
            return service.fetch_update_info()
        except Exception:
            return None

    future = _BG_POOL.submit(worker)

    def done(_future):
        try:
            info = _future.result()
        except Exception:
            info = None
        if info is None:
            return
        if not service.is_newer(info.version, APP_VERSION):
            return
        wx.CallAfter(_on_bg_update_info, ctx, info)

    future.add_done_callback(done)


def _on_bg_update_info(ctx, info):
    frame = ctx.frame
    if frame is None:
        return
    if not frame.IsShown():
        return
    _process_update_info(ctx, info, show_latest=False)


def _check_yt_updates_bg(ctx):
    frame = ctx.frame
    if frame is None:
        return
    channel = str(ctx.settings.get_yt_dlp_channel() or "").strip().lower()

    def worker():
        try:
            yt_components.add_to_path()
            local_ver = str(yt_components.yt_local_version() or "").strip()
            if not local_ver:
                return None
            remote_ver, used_channel = yt_components.yt_remote_version(channel=channel)
            remote_ver = str(remote_ver or "").strip()
            if not remote_ver:
                return None
            return {
                "local": local_ver,
                "remote": remote_ver,
                "channel": str(used_channel or channel or "stable"),
            }
        except Exception:
            return None

    future = _BG_POOL.submit(worker)

    def done(_future):
        try:
            info = _future.result()
        except Exception:
            info = None
        if not info:
            return
        if not service.is_newer(info.get("remote"), info.get("local")):
            return
        wx.CallAfter(_on_bg_yt_update_info, ctx, info)

    future.add_done_callback(done)


def _on_bg_yt_update_info(ctx, info):
    frame = ctx.frame
    if frame is None:
        return
    if not frame.IsShown():
        return
    local_ver = str(info.get("local") or "").strip() or _("unknown")
    remote_ver = str(info.get("remote") or "").strip() or _("unknown")
    channel = str(info.get("channel") or "stable").strip() or "stable"
    message = _(
        "A newer yt-dlp version is available on '{ch}' channel.\n"
        "Current version: {cur}\n"
        "Latest version: {new}\n\n"
        "Do you want to update now?"
    ).format(
        ch=channel,
        cur=local_ver,
        new=remote_ver,
    )
    answer = wx.MessageBox(
        message,
        _("yt-dlp update"),
        wx.YES_NO | wx.ICON_QUESTION,
        parent=frame,
    )
    if answer == wx.YES:
        update_youtube_components_now(ctx)


def _fetch_info(parent):
    def job(cancel, _on_line, _on_up):
        if cancel.is_set():
            raise service.CancelledError()
        return service.fetch_update_info()

    out = _run_busy(parent, _("Checking for app updates"), job)
    if out["cancelled"] or not out["ok"]:
        return None
    return out["value"]


def _launch_updater(asset_path):
    base = service.app_dir()
    updater = service.updater_path(base)
    if not os.path.isfile(updater):
        return False
    try:
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        pid = os.getpid()
        subprocess.Popen(
            [updater, asset_path, base, str(pid)],
            cwd=base,
            creationflags=creationflags,
        )
        return True
    except Exception:
        return False


def _run_busy(parent, title, job, on_line_ui=None):
    dlg = BusyDialog(parent, title, title)
    return _run_with_dialog(dlg, job, simple=True, on_line_ui=on_line_ui)


def _run_task(parent, title, job, fmt_up=None, label=""):
    dlg = TaskDialog(parent, title, label=label)
    return _run_with_dialog(dlg, job, fmt_up=fmt_up, simple=False)


def _run_with_dialog(dlg, job, fmt_up=None, simple=False, on_line_ui=None):
    updates = queue.Queue()
    cancel = service.CancelFlag()
    state = {
        "done": False,
        "ok": False,
        "value": None,
        "error": "",
        "cancelled": False,
    }

    def on_line(text):
        updates.put(("line", str(text)))

    def on_up(data):
        updates.put(("up", data))

    def worker():
        try:
            value = job(cancel, on_line, on_up)
            return {"ok": True, "value": value, "error": "", "cancelled": False}
        except service.CancelledError:
            return {"ok": False, "value": None, "error": "", "cancelled": True}
        except Exception as exc:
            return {
                "ok": False,
                "value": None,
                "error": str(exc),
                "cancelled": cancel.is_set(),
            }

    pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = pool.submit(worker)
    timer = wx.Timer(dlg)

    def on_tick(_event):
        if dlg.was_cancelled() and not state["done"]:
            cancel.set()
            state["done"] = True
            state["ok"] = False
            state["value"] = None
            state["error"] = ""
            state["cancelled"] = True
            dlg.EndModal(wx.ID_CANCEL)
            return
        saw_pct = False
        while True:
            try:
                kind, payload = updates.get_nowait()
            except queue.Empty:
                break
            if kind == "line":
                if simple:
                    dlg.set_label(payload)
                else:
                    dlg.append(payload)
                if on_line_ui is not None:
                    try:
                        on_line_ui(payload)
                    except Exception:
                        pass
            elif kind == "up":
                if isinstance(payload, dict) and "pct" in payload:
                    dlg.set_progress(payload.get("pct", 0.0))
                    saw_pct = True
                if not simple and fmt_up is not None and isinstance(payload, dict):
                    dlg.set_text(fmt_up(payload))
        if simple and not saw_pct:
            dlg.pulse()
        if future.done() and not state["done"]:
            state["done"] = True
            try:
                result = future.result()
            except Exception as exc:
                result = {
                    "ok": False,
                    "value": None,
                    "error": str(exc),
                    "cancelled": cancel.is_set(),
                }
            state["ok"] = bool(result.get("ok"))
            state["value"] = result.get("value")
            state["error"] = str(result.get("error") or "")
            state["cancelled"] = bool(result.get("cancelled")) or cancel.is_set()
            if state["ok"]:
                dlg.set_progress(100.0)
            dlg.EndModal(wx.ID_OK if state["ok"] else wx.ID_CANCEL)

    dlg.Bind(wx.EVT_TIMER, on_tick, timer)
    timer.Start(50)
    dlg.ShowModal()
    timer.Stop()
    if not state["done"] and future.done():
        try:
            result = future.result()
        except Exception as exc:
            result = {
                "ok": False,
                "value": None,
                "error": str(exc),
                "cancelled": cancel.is_set(),
            }
        state["done"] = True
        state["ok"] = bool(result.get("ok"))
        state["value"] = result.get("value")
        state["error"] = str(result.get("error") or "")
        state["cancelled"] = bool(result.get("cancelled")) or cancel.is_set()
    if state["cancelled"] and not future.done():
        pool.shutdown(wait=False, cancel_futures=False)
    else:
        pool.shutdown(wait=True, cancel_futures=True)
    dlg.Destroy()
    return state


def _fmt_update_status(data):
    size = service.fmt_bytes(data.get("size", 0))
    got = service.fmt_bytes(data.get("downloaded", 0))
    pct = float(data.get("pct", 0.0))
    return _("Total size: {size}\nDownloaded: {got}\nPercentage: {pct:.2f}%").format(
        size=size,
        got=got,
        pct=pct,
    )


def _fmt_yt_status(data):
    name = str(data.get("name", "") or "")
    ver = str(data.get("version", "") or "")
    channel = str(data.get("channel", "") or "")
    step = int(data.get("step", 0) or 0)
    total = int(data.get("total", 0) or 0)
    title = f"Downloading {name} {step} of {total}"
    if channel:
        title = f"{title} [{channel}]"
    if ver:
        title = f"{title} ({ver})"
    size = service.fmt_bytes(data.get("size", 0))
    got = service.fmt_bytes(data.get("downloaded", 0))
    pct = float(data.get("pct", 0.0))
    return f"{title}\nTotal size: {size}\nDownloaded: {got}\nPercentage: {pct:.2f}%"
