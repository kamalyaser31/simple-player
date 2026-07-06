import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from urllib import request

from config.constants import (
    APP_UPDATE_ASSET_TEMPLATE,
    APP_UPDATE_INFO_URL,
    APP_UPDATE_INSTALLER_EXT,
    APP_UPDATE_INSTALLER_MARKER,
    APP_UPDATE_PORTABLE_EXT,
    APP_UPDATE_RELEASES_URL,
    APP_UPDATE_UPDATER_EXE,
)
from helpers.http_utils import open_url


UA = "SimpleAudioPlayer/1.0"


class CancelledError(Exception):
    pass


class CancelFlag:
    def __init__(self):
        self._cancelled = False

    def set(self):
        self._cancelled = True

    def is_set(self):
        return bool(self._cancelled)


@dataclass
class UpdateInfo:
    version: str
    changes: str


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def is_installer_mode(base_dir=None):
    root = base_dir or app_dir()
    marker = os.path.join(root, APP_UPDATE_INSTALLER_MARKER)
    return os.path.isfile(marker)


def updater_path(base_dir=None):
    root = base_dir or app_dir()
    return os.path.join(root, APP_UPDATE_UPDATER_EXE)


def asset_ext(installer_mode):
    return APP_UPDATE_INSTALLER_EXT if installer_mode else APP_UPDATE_PORTABLE_EXT


def asset_name(version, installer_mode):
    ext = asset_ext(installer_mode)
    return APP_UPDATE_ASSET_TEMPLATE.format(version=version, ext=ext)


def asset_url(version, installer_mode):
    tag = f"v{version}"
    name = asset_name(version, installer_mode)
    return f"{APP_UPDATE_RELEASES_URL}/{tag}/{name}"


def temp_download_path(version, installer_mode):
    suffix = "." + asset_ext(installer_mode)
    name = f"sap_update_{version}{suffix}"
    return os.path.join(tempfile.gettempdir(), name)


def parse_info_json(payload):
    if not isinstance(payload, dict):
        raise ValueError("Invalid info payload.")
    version = str(payload.get("version") or "").strip()
    if not version:
        raise ValueError("Missing version in info.json")
    changes = payload.get("changes")
    if isinstance(changes, list):
        changes = "\n".join(str(item) for item in changes)
    return UpdateInfo(version=version, changes=str(changes or ""))


def fetch_update_info(url=None, timeout=12):
    target = str(url or APP_UPDATE_INFO_URL).strip()
    if not target:
        raise ValueError("Update info URL is not configured.")
    req = request.Request(target, headers={"User-Agent": UA})
    with open_url(req, timeout=timeout) as resp:
        raw = resp.read()
    data = json.loads(raw.decode("utf-8", errors="replace"))
    return parse_info_json(data)


def is_newer(remote_version, local_version):
    return _cmp_ver(remote_version, local_version) > 0


def _cmp_ver(left, right):
    a = _ver_parts(left)
    b = _ver_parts(right)
    n = max(len(a), len(b))
    for i in range(n):
        x = a[i] if i < len(a) else 0
        y = b[i] if i < len(b) else 0
        if x < y:
            return -1
        if x > y:
            return 1
    return 0


def _ver_parts(text):
    raw = str(text or "")
    nums = [int(n) for n in re.findall(r"\d+", raw)]
    return nums or [0]


def download_file(url, dest, cancel, on_update=None, timeout=25):
    target = str(dest or "").strip()
    if not target:
        raise ValueError("Invalid destination path.")
    os.makedirs(os.path.dirname(target) or app_dir(), exist_ok=True)

    req = request.Request(url, headers={"User-Agent": UA})
    got = 0
    size = 0
    with open_url(req, timeout=timeout) as resp:
        size = int(resp.headers.get("Content-Length", "0") or "0")
        _emit(on_update, size, got)
        with open(target, "wb") as out:
            while True:
                if cancel.is_set():
                    raise CancelledError()
                chunk = resp.read(1024 * 64)
                if not chunk:
                    break
                out.write(chunk)
                got += len(chunk)
                _emit(on_update, size, got)
    _emit(on_update, size, got)
    return target


def _emit(on_update, size, got):
    if on_update is None:
        return
    pct = 0.0
    if size > 0:
        pct = min(100.0, (got / size) * 100.0)
    on_update(
        {
            "size": int(size),
            "downloaded": int(got),
            "pct": float(pct),
        }
    )


def fmt_bytes(value):
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
