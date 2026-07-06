import concurrent.futures
import queue
import wx
from gettext import gettext as _

from ui.task_dialogs import TaskDlg
from ui.yt_dialogs import MissingDlg
from .components import (
    CancelFlag,
    CancelledError,
    add_to_path,
    has_all,
    install_missing,
)


def check_startup(parent, settings):
    add_to_path()
    if has_all() or settings.get_yt_skip_prompt():
        return

    dlg = MissingDlg(parent)
    res = dlg.ShowModal()
    skip = dlg.skip_next()
    dlg.Destroy()

    if skip:
        settings.set_yt_skip_prompt(True)
        settings.save()
    if res != wx.ID_YES:
        return

    ok, canceled, err = _run_install(parent, settings)
    if canceled:
        return
    if not ok:
        _show_install_error(parent, err)


def install_components_now(parent, settings, channel=None):
    add_to_path()
    if has_all():
        wx.MessageBox(
            _("YouTube components are already installed."),
            _("Info"),
            wx.OK | wx.ICON_INFORMATION,
            parent=parent,
        )
        return True

    ok, canceled, err = _run_install(parent, settings, channel=channel)
    if canceled:
        return False
    if not ok:
        _show_install_error(parent, err)
        return False

    wx.MessageBox(
        _("YouTube components were downloaded successfully."),
        _("Success"),
        wx.OK | wx.ICON_INFORMATION,
        parent=parent,
    )
    return True


def _run_install(parent, settings, channel=None):
    dlg = TaskDlg(parent, _("Downloading YouTube components"))
    dlg.set_progress(0.0)
    updates = queue.Queue()
    cancel = CancelFlag()
    state = {"done": False, "ok": False, "err": "", "canceled": False}

    def on_update(data):
        updates.put(("u", data))

    def worker():
        try:
            sel_channel = str(channel or settings.get_yt_dlp_channel() or "").strip()
            ok = install_missing(cancel, on_update, channel=sel_channel)
            return {"ok": ok, "err": "", "canceled": False}
        except CancelledError:
            return {"ok": False, "err": "", "canceled": True}
        except Exception as exc:
            return {"ok": False, "err": str(exc), "canceled": cancel.is_set()}

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(worker)
        timer = wx.Timer(dlg)

        def on_tick(_event):
            if dlg.was_cancelled():
                cancel.set()
            while True:
                try:
                    kind, payload = updates.get_nowait()
                except queue.Empty:
                    break
                if kind == "u":
                    dlg.set_text(_fmt_status(payload))
                    dlg.set_progress(payload.get("pct", 0.0))
            if future.done() and not state["done"]:
                state["done"] = True
                try:
                    result = future.result()
                except Exception as exc:
                    result = {"ok": False, "err": str(exc), "canceled": cancel.is_set()}
                state["ok"] = bool(result.get("ok"))
                state["err"] = result.get("err", "")
                state["canceled"] = bool(result.get("canceled")) or cancel.is_set()
                if state["ok"]:
                    dlg.set_progress(100.0)
                dlg.EndModal(wx.ID_OK if state["ok"] else wx.ID_CANCEL)

        dlg.Bind(wx.EVT_TIMER, on_tick, timer)
        timer.Start(50)
        dlg.ShowModal()
        timer.Stop()
    dlg.Destroy()
    add_to_path()
    return state["ok"], state["canceled"], state["err"]


def _fmt_status(data):
    name = data.get("name", "")
    ver = data.get("version", "")
    title = f"Downloading {name} {data.get('step', 0)} of {data.get('total', 0)}"
    if ver:
        title = f"{title} ({ver})"
    size = _fmt_bytes(data.get("size", 0))
    got = _fmt_bytes(data.get("downloaded", 0))
    pct = f"{float(data.get('pct', 0.0)):.2f}%"
    return f"{title}\nTotal size: {size}\nDownloaded: {got}\nPercentage: {pct}"


def _fmt_bytes(value):
    try:
        num = int(value)
    except Exception:
        num = 0
    if num <= 0:
        return "Unknown"
    size = float(num)
    units = ("B", "KB", "MB", "GB", "TB")
    idx = 0
    while size >= 1024.0 and idx < len(units) - 1:
        size /= 1024.0
        idx += 1
    if idx == 0:
        return f"{int(size)} {units[idx]}"
    return f"{size:.2f} {units[idx]}"


def _show_install_error(parent, err):
    message = _("Could not install YouTube components.")
    if err:
        message = f"{message}\n{err}"
    wx.MessageBox(message, _("Error"), wx.OK | wx.ICON_ERROR, parent=parent)
