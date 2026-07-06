import json
import os
import subprocess
import threading
from dataclasses import dataclass
from gettext import gettext as _
from urllib.parse import parse_qs, urlparse

from .components import CancelledError, add_to_path, deno_runtime, yt_path


@dataclass
class YtItem:
    title: str
    url: str
    channel_url: str
    channel_name: str
    description: str = ""


@dataclass
class InspectResult:
    kind: str
    title: str
    items: list


class ResolveError(Exception):
    pass


FMT_SEL = "bestaudio[ext=m4a]/bestaudio/best"
FMT_VIDEO_LOW = "best[height<=?360][ext=mp4]/best[height<=?360]/best[ext=mp4]/best"
FMT_VIDEO_MED = "best[height<=?720][ext=mp4]/best[height<=?720]/best[ext=mp4]/best"
FMT_VIDEO_BEST = "best[ext=mp4]/best"
_ERR_CTX = threading.local()


def inspect_link(link, cancel, on_line=None):
    link = str(link or "").strip()
    if not link:
        raise ResolveError(_("Invalid link."))
    if _is_channel(link):
        return InspectResult(kind="channel", title="", items=[])

    exe = yt_path()
    if not os.path.isfile(exe):
        raise ResolveError(_("yt-dlp is not available."))

    add_to_path()
    if _is_playlist(link):
        _log(on_line, _("Loading playlist items..."))
        items, title = _playlist_items(exe, link, cancel)
        return InspectResult(kind="playlist", title=title, items=items)

    _log(on_line, _("Loading video details..."))
    item = _single_item(exe, link, cancel)
    if item is None:
        raise ResolveError(_("No playable YouTube items were found."))
    return InspectResult(kind="video", title=item.title, items=[item])


def format_selector(audio_only=True, quality="medium"):
    if bool(audio_only):
        return FMT_SEL
    mode = str(quality or "medium").strip().lower()
    if mode == "low":
        return FMT_VIDEO_LOW
    if mode == "best":
        return FMT_VIDEO_BEST
    return FMT_VIDEO_MED


def resolve_stream(item_url, cancel, on_line=None, audio_only=True, quality="medium"):
    exe = yt_path()
    if not os.path.isfile(exe):
        raise ResolveError(_("yt-dlp is not available."))
    add_to_path()
    _log(on_line, _("Fetching stream URL..."))
    fmt = format_selector(audio_only=audio_only, quality=quality)

    data_args = _base(exe) + [
        "--no-playlist",
        "--dump-single-json",
        "-f",
        fmt,
        item_url,
    ]
    data = _run_json(data_args, cancel)
    if isinstance(data, dict):
        url = _pick_stream(data)
        if url:
            return url
    diag = _get_diag()

    args = _base(exe) + [
        "--no-playlist",
        "-g",
        "-f",
        fmt,
        item_url,
    ]
    lines = _run_lines(args, cancel)
    if lines:
        return lines[0]
    diag = _get_diag() or diag

    fallback = _base(exe) + ["--no-playlist", "-g", item_url]
    lines = _run_lines(fallback, cancel)
    if lines:
        return lines[0]
    diag = _get_diag() or diag
    raise ResolveError(_with_diag(_("Could not resolve a playable stream."), diag))


def fetch_item(item_url, cancel, on_line=None):
    exe = yt_path()
    if not os.path.isfile(exe):
        raise ResolveError(_("yt-dlp is not available."))
    add_to_path()
    _log(on_line, _("Loading video details..."))
    item = _single_item(exe, item_url, cancel)
    if item is None:
        raise ResolveError(
            _with_diag(_("Could not read video details."), _get_diag())
        )
    return item


def fetch_play(item_url, cancel, on_line=None, audio_only=True, quality="medium"):
    exe = yt_path()
    if not os.path.isfile(exe):
        raise ResolveError(_("yt-dlp is not available."))
    add_to_path()
    _log(on_line, _("Loading YouTube stream..."))
    fmt = format_selector(audio_only=audio_only, quality=quality)

    args = _base(exe) + [
        "--no-playlist",
        "--dump-single-json",
        "-f",
        fmt,
        item_url,
    ]
    data = _run_json(args, cancel)
    item = None
    stream = ""
    if isinstance(data, dict):
        item = _item_from_data(data, item_url)
        stream = _pick_stream(data)

    if item is None:
        item = _single_item(exe, item_url, cancel)
    if item is None:
        raise ResolveError(
            _with_diag(_("Could not read video details."), _get_diag())
        )
    if not stream:
        stream = resolve_stream(
            item.url or item_url,
            cancel,
            on_line=on_line,
            audio_only=audio_only,
            quality=quality,
        )
    return {"item": item, "stream": stream}


def _playlist_items(exe, link, cancel):
    args = _base(exe) + [
        "--flat-playlist",
        "--dump-single-json",
        "--ignore-errors",
        link,
    ]
    data = _run_json(args, cancel)
    if not isinstance(data, dict):
        raise ResolveError(
            _with_diag(_("Could not read playlist information."), _get_diag())
        )
    title = str(data.get("title") or "").strip()
    entries = data.get("entries") or []
    out = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        item = _entry_to_item(entry)
        if item is not None:
            out.append(item)
    if not out:
        raise ResolveError(_("No videos were found in this playlist."))
    return out, title


def _single_item(exe, link, cancel):
    args = _base(exe) + ["--no-playlist", "--dump-single-json", link]
    data = _run_json(args, cancel)
    if not isinstance(data, dict):
        return None
    return _item_from_data(data, link)


def _entry_to_item(entry):
    title = str(entry.get("title") or "").strip()
    channel_url = str(entry.get("channel_url") or entry.get("uploader_url") or "").strip()
    channel_name = str(entry.get("channel") or entry.get("uploader") or "").strip()

    url = str(entry.get("webpage_url") or "").strip()
    if not url:
        raw = str(entry.get("url") or "").strip()
        vid = str(entry.get("id") or "").strip()
        if raw and raw.startswith("http"):
            url = raw
        elif vid:
            url = f"https://www.youtube.com/watch?v={vid}"
        elif raw:
            url = f"https://www.youtube.com/watch?v={raw}"
    if not url:
        return None
    if not title:
        title = url
    desc = str(entry.get("description") or "").strip()
    return YtItem(
        title=title,
        url=url,
        channel_url=channel_url,
        channel_name=channel_name,
        description=desc,
    )


def _item_from_data(data, fallback_link):
    item = _entry_to_item(data)
    if item is not None:
        return item
    url = str(data.get("webpage_url") or "").strip()
    if not url:
        url = fallback_link
    title = str(data.get("title") or "").strip() or url
    channel_url = str(data.get("channel_url") or data.get("uploader_url") or "").strip()
    channel_name = str(data.get("channel") or data.get("uploader") or "").strip()
    desc = str(data.get("description") or "").strip()
    return YtItem(
        title=title,
        url=url,
        channel_url=channel_url,
        channel_name=channel_name,
        description=desc,
    )


def _pick_stream(data):
    url = str(data.get("url") or "").strip()
    if url:
        return url
    req = data.get("requested_formats") or []
    if isinstance(req, list):
        for part in req:
            if not isinstance(part, dict):
                continue
            part_url = str(part.get("url") or "").strip()
            if part_url:
                return part_url
    return ""


def _run_json(args, cancel):
    lines = _run_lines(args, cancel)
    if not lines:
        return None
    raw = "\n".join(lines).strip()
    _raise_if_429(raw)
    try:
        return json.loads(raw)
    except Exception:
        if not _get_diag():
            _set_diag(_("yt-dlp returned invalid JSON data."))
        return None


def _run_lines(args, cancel):
    env = os.environ.copy()
    env["PATH"] = os.path.dirname(yt_path()) + os.pathsep + env.get("PATH", "")
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    proc = subprocess.Popen(
        args,
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
    while True:
        if cancel.is_set():
            try:
                proc.terminate()
            except Exception:
                pass
            try:
                proc.communicate(timeout=0.5)
            except Exception:
                pass
            raise CancelledError()
        try:
            out, err = proc.communicate(timeout=0.1)
            break
        except subprocess.TimeoutExpired:
            continue
    _raise_if_429(err)
    if proc.returncode not in (0, None):
        diag = _short_diag(err) or _short_diag(out)
        _set_diag(diag)
        return []
    _set_diag("")
    return [line.strip() for line in (out or "").splitlines() if line.strip()]


def _base(exe):
    args = [exe, "--no-warnings", "--extractor-args", "youtube:player_client=android"]
    runtime = deno_runtime()
    if runtime:
        args.extend(["--js-runtimes", runtime])
    return args


def _is_playlist(link):
    text = str(link or "").strip().lower()
    if "youtube.com/playlist" in text:
        return True
    try:
        parsed = urlparse(text)
        params = parse_qs(parsed.query or "")
    except Exception:
        return False
    return "list" in params and bool(params.get("list"))


def _is_channel(link):
    text = str(link or "").strip().lower()
    if "youtube.com/channel/" in text:
        return True
    if "youtube.com/@" in text and "watch?" not in text and "playlist?" not in text:
        return True
    return False


def _log(on_line, text):
    if on_line is not None:
        on_line(str(text))


def _raise_if_429(text):
    low = str(text or "").lower()
    if "http error 429" in low or "too many requests" in low:
        raise ResolveError(
            _(
                "YouTube returned HTTP 429 (Too Many Requests). "
                "Your IP may be temporarily rate-limited."
            )
        )


def _set_diag(text):
    _ERR_CTX.last = str(text or "").strip()


def _get_diag():
    return str(getattr(_ERR_CTX, "last", "") or "").strip()


def _short_diag(text):
    raw = str(text or "").strip()
    if not raw:
        return ""
    line = raw.splitlines()[0].strip()
    if len(line) > 220:
        line = line[:220].rstrip() + "..."
    return line


def _with_diag(base, diag):
    msg = str(base or "")
    detail = str(diag or "").strip()
    if not detail:
        return msg
    return _("{base}\nDetails: {details}").format(base=msg, details=detail)
