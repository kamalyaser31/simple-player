import os
from urllib.parse import urlparse


def set_ready(ctx):
    ctx.reset_selection()
    ctx.set_file_loaded(True)
    ctx.set_playing(True)


def set_switched(ctx):
    ctx.reset_selection()
    ctx.set_playing(True)


def set_empty(ctx):
    ctx.reset_selection()
    ctx.set_file_loaded(False)
    ctx.set_playing(False)


def open_mode(ctx, path):
    mode = ctx.settings.get_open_with_files_mode()
    if mode == "main_folder":
        ok = ctx.player.open_file_with_folder(path, recursive=False)
    elif mode == "main_and_subfolders":
        ok = ctx.player.open_file_with_folder(path, recursive=True)
    else:
        ok = ctx.player.open_file(path)
    if ok:
        set_ready(ctx)
    return ok


def res_clip(path):
    if not path:
        return ""
    p = os.path.expandvars(os.path.expanduser(path))
    p = os.path.abspath(p)
    if os.path.exists(p):
        return p
    return ""


def res_shell(path):
    if not path:
        return ""
    p = str(path).strip()
    if not p:
        return ""
    if p.startswith('"') and p.endswith('"') and len(p) >= 2:
        p = p[1:-1]
    return res_clip(p)


def is_http_url(value):
    parsed = urlparse(str(value or "").strip())
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def show_name(path):
    text = str(path or "")
    if is_http_url(text):
        parsed = urlparse(text)
        host = parsed.netloc or text
        tail = parsed.path.strip("/").split("/")[-1] if parsed.path else ""
        return f"{host}/{tail}" if tail else host
    return os.path.basename(text) or text
