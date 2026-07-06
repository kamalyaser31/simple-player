from urllib.parse import urlparse
import traceback

from .components import CancelFlag
from .resolver import YtItem


def mk_ses(kind, title, items, search=None):
    rows = [item for item in list(items or []) if isinstance(item, YtItem)]
    return {
        "kind": str(kind or ""),
        "title": str(title or ""),
        "items": rows,
        "sel": 0,
        "urls": {str(item.url or "") for item in rows},
        "search": search,
        "queued": set(),
        "next_jobs": {},
        "prep_jobs": {},
        "more_jobs": {},
        "pending_next": None,
        "cancel": CancelFlag(),
        "prep_keys": set(),
    }


def set_ses(ctx, ses, sel):
    prev = get_ses(ctx)
    if prev is not None and prev is not ses:
        _cancel_ses(prev)
    ses["sel"] = int(sel)
    ses["urls"] = {str(item.url or "") for item in ses.get("items", [])}
    ctx.yt_pl = ses


def get_ses(ctx):
    data = getattr(ctx, "yt_pl", None)
    if not isinstance(data, dict):
        return None
    if "items" not in data or "urls" not in data:
        return None
    return data


def clear_ses(ctx):
    ses = get_ses(ctx)
    if ses is not None:
        _cancel_ses(ses)
    ctx.yt_pl = None


def cleanup_ses(ctx, ses):
    if not isinstance(ses, dict):
        return
    _cancel_ses(ses)
    if get_ses(ctx) is ses:
        ctx.yt_pl = None


def sync_removed_sources(ses, sources):
    if not isinstance(ses, dict):
        return set()
    removed = {
        str(source or "").strip()
        for source in (sources or [])
        if str(source or "").strip()
    }
    if not removed:
        return set()
    queued = ses.setdefault("queued", set())
    if isinstance(queued, set):
        queued.difference_update(removed)
    pending = ses.get("pending_next")
    if isinstance(pending, dict):
        source = str(pending.get("source") or "").strip()
        key = str(pending.get("key") or "").strip()
        if source in removed or any(key.startswith(f"{item}|") for item in removed):
            ses["pending_next"] = None
    return removed


def _cancel_ses(ses):
    flag = ses.get("cancel")
    if flag is not None and hasattr(flag, "set"):
        try:
            flag.set()
        except Exception:
            traceback.print_exc()
    for group in ("next_jobs", "prep_jobs", "more_jobs"):
        jobs = ses.get(group)
        if not isinstance(jobs, dict):
            continue
        for future in list(jobs.values()):
            try:
                if future is not None and not future.done():
                    future.cancel()
            except Exception:
                traceback.print_exc()
        jobs.clear()


def ses_idx(ctx, ses):
    src = str(ctx.player.current_source or "").strip()
    if not src:
        return None
    items = ses.get("items", [])
    for idx, item in enumerate(items):
        if str(getattr(item, "url", "") or "") == src:
            return idx
    return None


def set_now(ctx, item):
    ctx.yt_now = {
        "url": str(getattr(item, "url", "") or ""),
        "title": str(getattr(item, "title", "") or ""),
        "desc": str(getattr(item, "description", "") or ""),
    }


def cur_url(ctx):
    return str(ctx.player.current_source or "").strip()


def is_yt(url):
    text = str(url or "").strip()
    if not text:
        return False
    try:
        host = (urlparse(text).netloc or "").lower()
    except Exception:
        host = ""
    return "youtube.com" in host or "youtu.be" in host
