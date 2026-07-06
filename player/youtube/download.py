import os
import re
import subprocess
from gettext import gettext as _

from .components import CancelledError, deno_runtime, yt_path


_DL_RE = re.compile(
    r"\[download\]\s+(?P<pct>\d+(?:\.\d+)?)%\s+of\s+(?P<size>[^\s]+)",
    re.IGNORECASE,
)


def dl_audio_m4a(source_url, folder, cancel, on_update=None):
    exe = yt_path()
    if not os.path.isfile(exe):
        raise RuntimeError(_("yt-dlp is not available."))
    if not folder or not os.path.isdir(folder):
        raise RuntimeError(_("Invalid download folder."))

    out_tpl = os.path.join(folder, "%(title)s.%(ext)s")
    args = [
        exe,
        "--newline",
        "--progress",
        "--no-warnings",
        "--no-playlist",
        "-x",
        "--audio-format",
        "m4a",
        "-o",
        out_tpl,
        source_url,
    ]
    runtime = deno_runtime()
    if runtime:
        args.extend(["--js-runtimes", runtime])

    env = os.environ.copy()
    env["PATH"] = os.path.dirname(exe) + os.pathsep + env.get("PATH", "")
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=creationflags,
        env=env,
    )
    try:
        for line in iter(proc.stdout.readline, ""):
            if cancel.is_set():
                _stop(proc)
                raise CancelledError()
            info = _parse(line)
            if info is not None:
                _emit(on_update, info)
        code = proc.wait()
        if cancel.is_set():
            _stop(proc)
            raise CancelledError()
        if code != 0:
            raise RuntimeError(_("Download failed."))
    finally:
        try:
            if proc.stdout:
                proc.stdout.close()
        except Exception:
            pass


def _emit(on_update, info):
    if on_update is not None:
        on_update(info)


def _parse(line):
    text = str(line or "").strip()
    m = _DL_RE.search(text)
    if not m:
        return None
    pct = float(m.group("pct"))
    total_text = m.group("size")
    total_b = _to_bytes(total_text)
    got_b = int(total_b * (pct / 100.0)) if total_b > 0 else 0
    return {
        "pct": pct,
        "total_text": total_text,
        "total_b": total_b,
        "got_b": got_b,
    }


def _to_bytes(text):
    raw = str(text or "").strip()
    if not raw:
        return 0
    unit_map = {
        "b": 1,
        "kb": 1000,
        "mb": 1000 * 1000,
        "gb": 1000 * 1000 * 1000,
        "tb": 1000 * 1000 * 1000 * 1000,
        "kib": 1024,
        "mib": 1024 * 1024,
        "gib": 1024 * 1024 * 1024,
        "tib": 1024 * 1024 * 1024 * 1024,
    }
    m = re.match(r"(?i)^\s*([0-9]+(?:\.[0-9]+)?)\s*([kmgt]?i?b)\s*$", raw)
    if not m:
        return 0
    val = float(m.group(1))
    unit = m.group(2).lower()
    mult = unit_map.get(unit, 0)
    return int(val * mult)


def _stop(proc):
    try:
        proc.terminate()
    except Exception:
        pass
