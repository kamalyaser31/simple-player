import concurrent.futures
import queue
from dataclasses import dataclass

import wx

from ui.task_dialogs import BusyDlg, TaskDlg
from .components import CancelFlag, CancelledError
from .resolver import ResolveError


@dataclass
class TaskOut:
    ok: bool
    val: object = None
    err: str = ""
    can: bool = False


def run_task(parent, title, job, fmt_up=None, simple=False):
    dlg = BusyDlg(parent, title, title) if simple else TaskDlg(parent, title)
    dlg.set_progress(0.0)
    updates = queue.Queue()
    cancel = CancelFlag()
    state = {"done": False, "ok": False, "val": None, "err": "", "can": False}

    def on_line(text):
        updates.put(("line", str(text)))

    def on_up(data):
        updates.put(("up", data))

    def worker():
        try:
            value = job(cancel, on_line, on_up)
            return {"ok": True, "val": value, "err": "", "can": False}
        except CancelledError:
            return {"ok": False, "val": None, "err": "", "can": True}
        except ResolveError as exc:
            return {"ok": False, "val": None, "err": str(exc), "can": cancel.is_set()}
        except Exception as exc:
            return {"ok": False, "val": None, "err": str(exc), "can": cancel.is_set()}

    pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = pool.submit(worker)
    timer = wx.Timer(dlg)

    def on_tick(_event):
        if dlg.was_cancelled() and not state["done"]:
            cancel.set()
            state["done"] = True
            state["ok"] = False
            state["val"] = None
            state["err"] = ""
            state["can"] = True
            dlg.EndModal(wx.ID_CANCEL)
            return
        saw_pct = False
        while True:
            try:
                kind, payload = updates.get_nowait()
            except queue.Empty:
                break
            if kind == "line":
                if not simple:
                    dlg.append(payload)
            elif kind == "up":
                if isinstance(payload, dict) and "pct" in payload:
                    dlg.set_progress(payload.get("pct", 0.0))
                    saw_pct = True
                if not simple:
                    if fmt_up is None:
                        dlg.append(str(payload))
                    else:
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
                    "val": None,
                    "err": str(exc),
                    "can": cancel.is_set(),
                }
            state["ok"] = bool(result.get("ok"))
            state["val"] = result.get("val")
            state["err"] = str(result.get("err", "") or "")
            state["can"] = bool(result.get("can")) or cancel.is_set()
            if state["ok"]:
                dlg.set_progress(100.0)
            dlg.EndModal(wx.ID_OK if state["ok"] else wx.ID_CANCEL)

    dlg.Bind(wx.EVT_TIMER, on_tick, timer)
    timer.Start(50)
    dlg.ShowModal()
    timer.Stop()
    dlg.Destroy()
    if not state["done"] and future.done():
        try:
            result = future.result()
        except Exception as exc:
            result = {
                "ok": False,
                "val": None,
                "err": str(exc),
                "can": cancel.is_set(),
            }
        state["done"] = True
        state["ok"] = bool(result.get("ok"))
        state["val"] = result.get("val")
        state["err"] = str(result.get("err", "") or "")
        state["can"] = bool(result.get("can")) or cancel.is_set()
    if state["can"] and not future.done():
        pool.shutdown(wait=False, cancel_futures=False)
    else:
        pool.shutdown(wait=True, cancel_futures=True)
    return TaskOut(
        ok=bool(state["ok"]),
        val=state["val"],
        err=state["err"],
        can=bool(state["can"]),
    )
