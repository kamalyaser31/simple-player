import ctypes
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile


WAIT_OBJECT_0 = 0x00000000
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
SYNCHRONIZE = 0x00100000


def _wait_for_pid(pid, timeout_s=180):
    if pid <= 0 or os.name != "nt":
        return True
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    open_process = kernel32.OpenProcess
    open_process.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    open_process.restype = ctypes.c_void_p
    wait_for_single = kernel32.WaitForSingleObject
    wait_for_single.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    wait_for_single.restype = ctypes.c_uint32
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = [ctypes.c_void_p]
    close_handle.restype = ctypes.c_int

    handle = open_process(SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION, 0, int(pid))
    if not handle:
        return True
    try:
        result = wait_for_single(handle, int(max(0, timeout_s) * 1000))
    finally:
        close_handle(handle)
    return result in (WAIT_OBJECT_0, 0x00000080)


def _payload_root(path):
    entries = [name for name in os.listdir(path) if name not in (".", "..")]
    if len(entries) != 1:
        return path
    root = os.path.join(path, entries[0])
    if os.path.isdir(root):
        return root
    return path


def _iter_files(root):
    for base, _dirs, files in os.walk(root):
        for name in files:
            yield os.path.join(base, name)


def _restart_app(install_dir):
    exe = os.path.join(install_dir, "SimpleAudioPlayer.exe")
    if not os.path.isfile(exe):
        exe = os.path.join(install_dir, "main.exe")
    if not os.path.isfile(exe):
        return
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        subprocess.Popen([exe], cwd=install_dir, creationflags=flags)
    except Exception:
        return


def _copy_payload(payload_root, install_dir):
    for src in _iter_files(payload_root):
        rel = os.path.relpath(src, payload_root)
        dst = os.path.join(install_dir, rel)
        if os.path.basename(dst).lower() == "updater.exe":
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    return True


def _apply_zip(asset_path, install_dir):
    with zipfile.ZipFile(asset_path, "r") as zf:
        temp_dir = tempfile.mkdtemp(prefix="sap_updater_")
        try:
            zf.extractall(temp_dir)
            root = _payload_root(temp_dir)
            return _copy_payload(root, install_dir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def _run_installer(asset_path, install_dir):
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen([asset_path], cwd=install_dir, creationflags=flags)


def _parse_args():
    if len(sys.argv) < 3:
        return "", "", 0
    asset_path = os.path.abspath(sys.argv[1])
    install_dir = os.path.abspath(sys.argv[2])
    pid = 0
    if len(sys.argv) >= 4:
        try:
            pid = int(str(sys.argv[3] or "0"))
        except Exception:
            pid = 0
    return asset_path, install_dir, pid


def _run():
    asset_path, install_dir, pid = _parse_args()
    if not asset_path or not install_dir:
        return 2
    if not os.path.isfile(asset_path):
        return 3
    if not os.path.isdir(install_dir):
        return 4

    if pid > 0:
        _wait_for_pid(pid, timeout_s=300)

    ext = os.path.splitext(asset_path)[1].lower()
    if ext == ".zip":
        if not _apply_zip(asset_path, install_dir):
            return 5
        _restart_app(install_dir)
        return 0
    if ext == ".exe":
        _run_installer(asset_path, install_dir)
        return 0
    return 6


if __name__ == "__main__":
    try:
        raise SystemExit(_run())
    except Exception:
        raise SystemExit(1)
