import concurrent.futures
import os
import queue
import threading
import time

from gettext import gettext as _

import mpv
import wx

from helpers.file_helpers import show_name
from ui import dialogs
from helpers.utils import format_time


_DUR = {}
_DUR_LOCK = threading.Lock()
_PROBE_TO = 1.2
_LOADERS = set()


def show(parent_dlg, ctx, files):
    job = InfoJob(parent_dlg, ctx, files)
    _LOADERS.add(job)
    try:
        job.start()
    except Exception:
        _LOADERS.discard(job)
        ctx.speak(_("Could not load playlist info."), _("Info failed."))


class InfoJob:
    TICK_MS = 50

    def __init__(self, parent_dlg, ctx, files):
        self._parent_dlg = parent_dlg
        self._ctx = ctx
        self._files = list(files or [])
        self._q = queue.Queue()
        self._stop = threading.Event()
        self._pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._fut = None
        self._tmr = None
        self._tmr_owner = None
        self._bar = None
        self._value = 0
        self._done = False
        self._owner_destroyed = False

    def start(self):
        parent = self._ctx.frame if self._ctx.frame is not None else self._parent_dlg
        total = max(1, len(self._files))
        self._bar = wx.ProgressDialog(
            _("Loading playlist info"),
            _("Preparing..."),
            maximum=total,
            parent=parent,
            style=wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE,
        )
        self._bar.Update(0, _("Preparing..."))
        self._bar.Raise()

        cur_path = self._ctx.player.current_path
        cur_dur = self._ctx.player.get_duration()
        self._fut = self._pool.submit(
            scan,
            self._files,
            cur_path,
            cur_dur,
            self._q,
            self._stop,
        )
        self._fut.add_done_callback(self._on_future_done)
        self._tmr = wx.Timer(parent)
        self._tmr_owner = parent
        parent.Bind(wx.EVT_TIMER, self.on_tick, self._tmr)
        parent.Bind(wx.EVT_WINDOW_DESTROY, self.on_owner_destroy)
        self._tmr.Start(self.TICK_MS)

    def on_tick(self, _event):
        if self._done:
            return
        self.pull()
        if self._fut is not None and self._fut.done():
            self.finish(show_dialog=not self._owner_destroyed)

    def on_owner_destroy(self, event):
        try:
            obj = event.GetEventObject()
        except Exception:
            obj = None
        if self._tmr_owner is not None and obj is self._tmr_owner:
            self._owner_destroyed = True
            self._stop.set()
            self.finish(show_dialog=False)
        event.Skip()

    def _on_future_done(self, _future):
        try:
            wx.CallAfter(self._finish_from_future)
        except Exception:
            self._stop.set()
            self.finish(show_dialog=False)

    def _finish_from_future(self):
        if self._done:
            return
        self.finish(show_dialog=not self._owner_destroyed)

    def pull(self):
        while True:
            try:
                value, _total, name = self._q.get_nowait()
            except queue.Empty:
                break
            self._value = max(self._value, int(value))
            if self._bar is None:
                continue
            keep, _skip = self._bar.Update(
                self._value,
                _("Reading: {name}").format(name=name),
            )
            if not keep:
                self._stop.set()

    def finish(self, show_dialog=True):
        if self._done:
            return
        self._done = True
        try:
            if self._tmr is not None:
                self._tmr.Stop()
        except Exception:
            pass
        try:
            if self._tmr_owner is not None and self._tmr is not None:
                self._tmr_owner.Unbind(wx.EVT_TIMER, handler=self.on_tick, source=self._tmr)
        except Exception:
            pass
        try:
            if self._tmr_owner is not None:
                self._tmr_owner.Unbind(wx.EVT_WINDOW_DESTROY, handler=self.on_owner_destroy)
        except Exception:
            pass

        self.pull()
        info = None
        try:
            if self._fut is not None and self._fut.done():
                info = self._fut.result(timeout=0)
            else:
                if self._fut is not None:
                    try:
                        self._fut.cancel()
                    except Exception:
                        pass
        except Exception:
            info = None
        finally:
            try:
                self._pool.shutdown(wait=False, cancel_futures=False)
            except Exception:
                pass
            if self._bar is not None:
                try:
                    self._bar.Destroy()
                except Exception:
                    pass

        _LOADERS.discard(self)
        if not show_dialog:
            return
        if not info or info.get("cancelled"):
            return

        text = build_text(self._ctx, self._files, info)
        parent = self._parent_dlg
        if parent is None or (hasattr(parent, "IsBeingDeleted") and parent.IsBeingDeleted()):
            parent = self._ctx.frame
        if parent is None or (hasattr(parent, "IsBeingDeleted") and parent.IsBeingDeleted()):
            return
        dlg = dialogs.TextInfoDialog(parent, _("Playlist Info"), text)
        dlg.ShowModal()
        dlg.Destroy()


def scan(files, cur_path, cur_dur, q, stop):
    size = 0
    durs = []
    probe = None
    try:
        total = len(files)
        for idx, path in enumerate(files, start=1):
            if stop.is_set():
                break
            size += _size(path)
            dur, probe = _dur(path, cur_path, cur_dur, probe)
            durs.append(dur)
            q.put((idx, total, show_name(path)))
    finally:
        if probe is not None:
            try:
                probe.terminate()
            except Exception:
                pass
    return {"cancelled": stop.is_set(), "size": size, "durs": durs}


def build_text(ctx, files, info):
    durs = list(info.get("durs", []))
    idx = ctx.player.get_current_index()
    cur_elapsed = _sec(ctx.player.get_elapsed())
    cur_remain = _sec(ctx.player.get_remaining())

    total_dur = _sum(durs)
    elapsed = _elapsed(durs, idx, cur_elapsed)
    remain = _remain(durs, idx, cur_elapsed, cur_remain)

    lines = [
        _("Number of files: {count}").format(count=len(files)),
        _("Total size: {value}").format(value=_fmt_size(info.get("size", 0))),
        _("Total duration: {value}").format(value=_fmt_time(total_dur)),
        _("Elapsed: {value}").format(value=_fmt_time(elapsed)),
        _("Remaining: {value}").format(value=_fmt_time(remain)),
    ]
    return "\n".join(lines)


def _dur(path, cur_path, cur_dur, probe):
    if path == cur_path and _ok(cur_dur):
        val = float(cur_dur)
        _set(path, val)
        return val, probe

    cached = _get(path)
    if _ok(cached):
        return float(cached), probe

    if not os.path.isfile(path):
        return None, probe

    if probe is None:
        probe = _mk_probe()
        if probe is None:
            return None, None

    val = _probe(probe, path)
    if _ok(val):
        val = float(val)
        _set(path, val)
        return val, probe
    return None, probe


def _mk_probe():
    opts = {
        "vid": "no",
        "vo": "null",
        "ao": "null",
        "keep_open": "no",
        "input_default_bindings": False,
        "input_vo_keyboard": False,
        "osc": False,
        "idle": "yes",
    }
    try:
        return mpv.MPV(**opts)
    except Exception:
        return None


def _probe(probe, path):
    try:
        probe.command("loadfile", path, "replace", "pause=yes")
    except Exception:
        return None
    end = time.time() + _PROBE_TO
    while time.time() < end:
        val = getattr(probe, "duration", None)
        if _ok(val):
            try:
                probe.command("stop")
            except Exception:
                pass
            return float(val)
        time.sleep(0.05)
    try:
        probe.command("stop")
    except Exception:
        pass
    return None


def _elapsed(durs, idx, cur):
    if cur is None:
        return None
    if idx < 0 or idx >= len(durs):
        return None
    head = durs[:idx]
    if any(not _ok(v) for v in head):
        return None
    return sum(head) + cur


def _remain(durs, idx, cur, fallback):
    if idx < 0 or idx >= len(durs):
        return None
    cur_dur = durs[idx]
    if _ok(cur_dur) and cur is not None:
        cur_left = max(0.0, float(cur_dur) - float(cur))
    else:
        cur_left = fallback
    if cur_left is None:
        return None
    tail = durs[idx + 1 :]
    if any(not _ok(v) for v in tail):
        return None
    return cur_left + sum(tail)


def _sum(durs):
    vals = [float(v) for v in durs if _ok(v)]
    if not vals:
        return None
    return sum(vals)


def _size(path):
    if not os.path.isfile(path):
        return 0
    try:
        return int(os.path.getsize(path))
    except OSError:
        return 0


def _key(path):
    if os.path.isfile(path):
        return os.path.normcase(os.path.abspath(path))
    return str(path or "").strip()


def _get(path):
    key = _key(path)
    if not key:
        return None
    with _DUR_LOCK:
        return _DUR.get(key)


def _set(path, val):
    if not _ok(val):
        return
    key = _key(path)
    if not key:
        return
    with _DUR_LOCK:
        _DUR[key] = float(val)


def _sec(value):
    try:
        num = float(value)
    except (TypeError, ValueError):
        return None
    if num < 0:
        return 0.0
    return num


def _ok(value):
    try:
        return value is not None and float(value) > 0
    except (TypeError, ValueError):
        return False


def _fmt_time(sec):
    text = format_time(sec)
    if text is None:
        return _("Unavailable")
    return text


def _fmt_size(num_bytes):
    if num_bytes <= 0:
        return "0 B"
    val = float(num_bytes)
    units = ("B", "KB", "MB", "GB", "TB")
    idx = 0
    while val >= 1024.0 and idx < len(units) - 1:
        val /= 1024.0
        idx += 1
    if idx == 0:
        return f"{int(val)} {units[idx]}"
    return f"{val:.2f} {units[idx]}"

