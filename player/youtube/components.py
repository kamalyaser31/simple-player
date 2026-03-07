import json
import os
import subprocess
import tempfile
import time
import zipfile
from urllib import request

from config.constants import YT_DLP_DEFAULT_CHANNEL, YT_DLP_UPDATE_CHANNELS
from helpers.http_utils import open_url


APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
YT_EXE = os.path.join(APP_DIR, "yt-dlp.exe")
DENO_EXE = os.path.join(APP_DIR, "deno.exe")
DENO_ZIP = os.path.join(APP_DIR, "deno.zip")
UA = "SimpleAudioPlayer/1.0"
YT_CHANNEL_REPOS = {
    "stable": "yt-dlp/yt-dlp",
    "nightly": "yt-dlp/yt-dlp-nightly-builds",
    "master": "yt-dlp/yt-dlp-master-builds",
}


class CancelledError(Exception):
    pass


class CancelFlag:
    def __init__(self):
        self._cancelled = False

    def set(self):
        self._cancelled = True

    def is_set(self):
        return bool(self._cancelled)


def yt_path():
    return YT_EXE


def deno_path():
    return DENO_EXE


def deno_runtime():
    path = deno_path()
    if not os.path.isfile(path):
        return ""
    norm = os.path.abspath(path).replace("\\", "/")
    return f"deno:{norm}"


def has_yt():
    return os.path.isfile(YT_EXE)


def has_deno():
    return os.path.isfile(DENO_EXE)


def has_all():
    return has_yt() and has_deno()


def missing():
    out = []
    if not has_yt():
        out.append("yt-dlp")
    if not has_deno():
        out.append("Deno")
    return out


def add_to_path():
    current = os.environ.get("PATH", "")
    parts = current.split(os.pathsep) if current else []
    if APP_DIR not in parts:
        os.environ["PATH"] = APP_DIR + os.pathsep + current


def latest_tag(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = request.Request(url, headers={"User-Agent": UA})
    try:
        with open_url(req, timeout=12) as resp:
            raw = resp.read()
    except Exception:
        return None
    try:
        data = json.loads(raw.decode("utf-8", errors="replace"))
    except Exception:
        return None
    return data.get("tag_name")


def yt_local_version(timeout=30):
    if not has_yt():
        return ""
    cancel = CancelFlag()
    try:
        text = _run_yt_cmd(cancel, ["--version"], timeout=timeout)
    except Exception:
        return ""
    return _clean_version(text)


def yt_remote_version(channel=YT_DLP_DEFAULT_CHANNEL):
    chan = _norm_channel(channel)
    repo = YT_CHANNEL_REPOS.get(chan, YT_CHANNEL_REPOS[YT_DLP_DEFAULT_CHANNEL])
    tag = latest_tag(repo)
    if not tag:
        return "", chan
    return _clean_version(tag), chan


def plan(channel=YT_DLP_DEFAULT_CHANNEL):
    chan = _norm_channel(channel)
    yt_repo = YT_CHANNEL_REPOS.get(chan, YT_CHANNEL_REPOS[YT_DLP_DEFAULT_CHANNEL])
    return [
        {
            "name": "yt-dlp",
            "repo": yt_repo,
            "url": f"https://github.com/{yt_repo}/releases/latest/download/yt-dlp.exe",
            "dest": YT_EXE,
            "zip": False,
            "channel": chan,
        },
        {
            "name": "Deno",
            "repo": "denoland/deno",
            "url": "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip",
            "dest": DENO_ZIP,
            "zip": True,
            "channel": "",
        },
    ]


def install_missing(cancel, on_update, channel=YT_DLP_DEFAULT_CHANNEL):
    items = []
    for item in plan(channel=channel):
        if item["name"] == "yt-dlp" and has_yt():
            continue
        if item["name"] == "Deno" and has_deno():
            continue
        items.append(item)

    total = len(items)
    if total == 0:
        add_to_path()
        return True

    for idx, item in enumerate(items, start=1):
        tag = latest_tag(item["repo"])
        _download_item(item, idx, total, tag, cancel, on_update)
        if item["zip"]:
            _extract_deno_zip(item["dest"], cancel)
    add_to_path()
    return has_all()


def update_all(cancel, on_update, channel=YT_DLP_DEFAULT_CHANNEL, on_line=None):
    chan = _norm_channel(channel)

    if cancel.is_set():
        raise CancelledError()

    if not has_yt():
        raise RuntimeError("yt-dlp is not available.")

    _line(on_line, f"Updating yt-dlp ({chan})...")
    result = _yt_self_update(cancel, chan, on_line)
    add_to_path()
    result["ok"] = has_yt()
    return result


def _yt_self_update(cancel, channel, on_line=None):
    exe = yt_path()
    if not os.path.isfile(exe):
        raise RuntimeError("yt-dlp is not available.")
    _line(on_line, "Checking current yt-dlp version...")
    old_ver = _run_yt_cmd(cancel, ["--version"], on_line=on_line, timeout=60)
    old_ver = _clean_version(old_ver)
    if old_ver:
        _line(on_line, f"Current version: {old_ver}")

    _line(on_line, f"Running yt-dlp update for '{channel}' channel...")
    update_text = _run_yt_cmd(
        cancel,
        ["--update-to", f"{channel}@latest"],
        on_line=on_line,
        timeout=300,
    )
    _line(on_line, "Checking updated yt-dlp version...")
    new_ver = _run_yt_cmd(cancel, ["--version"], on_line=on_line, timeout=60)
    new_ver = _clean_version(new_ver)
    if new_ver:
        _line(on_line, f"Updated version: {new_ver}")
    updated = bool(new_ver and old_ver and new_ver != old_ver)
    if not updated:
        low = str(update_text or "").lower()
        updated = "updated yt-dlp to" in low
    return {
        "channel": str(channel or ""),
        "old_version": old_ver or "",
        "new_version": new_ver or old_ver or "",
        "updated": bool(updated),
    }


def _run_yt_cmd(cancel, args, on_line=None, timeout=180):
    cmd = [yt_path()] + list(args or [])
    env = os.environ.copy()
    env["PATH"] = APP_DIR + os.pathsep + env.get("PATH", "")
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=creationflags,
        env=env,
    )
    out = ""
    err = ""
    start = time.monotonic()
    while True:
        if timeout and time.monotonic() - start > float(timeout):
            try:
                proc.terminate()
            except Exception:
                pass
            raise RuntimeError(f"yt-dlp command timed out after {int(timeout)} seconds.")
        if cancel.is_set():
            try:
                proc.terminate()
            except Exception:
                pass
            raise CancelledError()
        try:
            out, err = proc.communicate(timeout=0.1)
            break
        except subprocess.TimeoutExpired:
            continue
    if proc.returncode != 0:
        text = (err or out or "").strip()
        if not text:
            text = f"yt-dlp exited with code {proc.returncode}"
        raise RuntimeError(text)
    merged = "\n".join(part for part in ((out or "").strip(), (err or "").strip()) if part).strip()
    return merged


def _download_item(item, idx, total, tag, cancel, on_update):
    dest_dir = os.path.dirname(item["dest"]) or APP_DIR
    os.makedirs(dest_dir, exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(
        prefix="sap_yt_",
        suffix=".tmp",
        dir=dest_dir,
    )
    os.close(tmp_fd)
    url = item["url"]
    req = request.Request(url, headers={"User-Agent": UA})

    downloaded = 0
    size = 0
    try:
        with open_url(req, timeout=20) as resp:
            size = int(resp.headers.get("Content-Length", "0") or "0")
            _emit(
                on_update,
                item["name"],
                idx,
                total,
                tag,
                size,
                downloaded,
                channel=item.get("channel", ""),
            )
            with open(tmp_path, "wb") as out:
                while True:
                    if cancel.is_set():
                        raise CancelledError()
                    chunk = resp.read(1024 * 32)
                    if not chunk:
                        break
                    out.write(chunk)
                    downloaded += len(chunk)
                    _emit(
                        on_update,
                        item["name"],
                        idx,
                        total,
                        tag,
                        size,
                        downloaded,
                        channel=item.get("channel", ""),
                    )
        os.makedirs(dest_dir, exist_ok=True)
        if os.path.isfile(item["dest"]):
            os.remove(item["dest"])
        os.replace(tmp_path, item["dest"])
    except CancelledError:
        if os.path.isfile(tmp_path):
            os.remove(tmp_path)
        raise
    except Exception:
        if os.path.isfile(tmp_path):
            os.remove(tmp_path)
        raise


def _extract_deno_zip(zip_path, cancel):
    if cancel.is_set():
        raise CancelledError()
    if not os.path.isfile(zip_path):
        raise RuntimeError("Deno zip not found.")
    with zipfile.ZipFile(zip_path, "r") as zf:
        target = None
        for name in zf.namelist():
            if name.lower().endswith("deno.exe"):
                target = name
                break
        if not target:
            raise RuntimeError("deno.exe not found in archive.")
        if cancel.is_set():
            raise CancelledError()
        with zf.open(target) as src, open(DENO_EXE, "wb") as dst:
            while True:
                if cancel.is_set():
                    raise CancelledError()
                chunk = src.read(1024 * 64)
                if not chunk:
                    break
                dst.write(chunk)
    if os.path.isfile(zip_path):
        os.remove(zip_path)


def _emit(on_update, name, idx, total, tag, size, downloaded, channel=""):
    if on_update is None:
        return
    pct = 0.0
    if size > 0:
        pct = min(100.0, (downloaded / size) * 100.0)
    on_update(
        {
            "name": name,
            "step": idx,
            "total": total,
            "version": tag or "",
            "channel": str(channel or ""),
            "size": size,
            "downloaded": downloaded,
            "pct": pct,
        }
    )


def _norm_channel(channel):
    text = str(channel or YT_DLP_DEFAULT_CHANNEL).strip().lower()
    if text not in YT_DLP_UPDATE_CHANNELS:
        return YT_DLP_DEFAULT_CHANNEL
    return text


def _line(on_line, text):
    if on_line is not None:
        on_line(str(text or ""))


def _clean_version(text):
    raw = str(text or "").strip()
    if not raw:
        return ""
    line = raw.splitlines()[0].strip()
    if line.lower().startswith("yt-dlp"):
        line = line[len("yt-dlp") :].strip(" :-")
    return line
