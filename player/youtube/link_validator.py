from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse


@dataclass(frozen=True)
class LinkInfo:
    raw: str
    is_http: bool
    is_youtube: bool
    kind: str
    has_video: bool = False
    has_playlist: bool = False


def parse_link(value):
    text = str(value or "").strip()
    if not _is_http_strict(text):
        return LinkInfo(raw=text, is_http=False, is_youtube=False, kind="invalid")
    if not _is_youtube(text):
        return LinkInfo(raw=text, is_http=True, is_youtube=False, kind="stream")
    kind, has_video, has_playlist = _yt_meta(text)
    return LinkInfo(
        raw=text,
        is_http=True,
        is_youtube=True,
        kind=kind,
        has_video=has_video,
        has_playlist=has_playlist,
    )


def is_youtube_url(value):
    info = parse_link(value)
    return bool(info.is_youtube)


def _is_http_strict(text):
    low = str(text or "").strip().lower()
    if not (low.startswith("http://") or low.startswith("https://")):
        return False
    parsed = urlparse(text)
    return parsed.scheme.lower() in ("http", "https") and bool(parsed.netloc)


def _is_youtube(text):
    parsed = urlparse(text)
    host = _host(parsed.netloc)
    if host in ("youtu.be", "www.youtu.be"):
        return True
    if host == "youtube.com" or host.endswith(".youtube.com"):
        return True
    return False


def _yt_meta(text):
    parsed = urlparse(text)
    host = _host(parsed.netloc)
    path = str(parsed.path or "").strip("/")
    parts = [p for p in path.split("/") if p]
    params = parse_qs(parsed.query or "")

    has_video = False
    has_playlist = False

    list_id = str((params.get("list") or [""])[0] or "").strip()
    if list_id:
        has_playlist = True

    if host in ("youtu.be", "www.youtu.be"):
        if parts:
            has_video = True
        return ("video" if has_video else "invalid", has_video, has_playlist)

    video_id = str((params.get("v") or [""])[0] or "").strip()
    if video_id:
        has_video = True

    if parts and parts[0] in ("shorts", "embed", "live", "v"):
        if len(parts) >= 2 and str(parts[1] or "").strip():
            has_video = True

    if has_video:
        return ("video", has_video, has_playlist)

    if parts and parts[0] in ("channel", "c", "user"):
        if len(parts) >= 2 and str(parts[1] or "").strip():
            return ("channel", has_video, has_playlist)
    if parts and parts[0].startswith("@"):
        return ("channel", has_video, has_playlist)

    if parts and parts[0] == "playlist" and list_id:
        return ("playlist", has_video, has_playlist)
    if list_id:
        return ("playlist", has_video, has_playlist)

    if parts and parts[0] == "watch":
        return ("invalid", has_video, has_playlist)
    return ("video", has_video, has_playlist)


def _host(value):
    host = str(value or "").strip().lower()
    if "@" in host:
        host = host.rsplit("@", 1)[-1]
    if ":" in host:
        host = host.split(":", 1)[0]
    return host.rstrip(".")
