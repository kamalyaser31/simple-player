import concurrent.futures

import wx
from gettext import gettext as _

from .components import CancelFlag, CancelledError, add_to_path, has_all
from .link_validator import parse_link
from .results import show_res
from .resolver import ResolveError, YtItem, fetch_play, inspect_link
from .search import start_search
from .state import clear_ses, get_ses, mk_ses, ses_idx, set_now, set_ses
from .task_ui import run_task
from .ui_utils import ask_link, ask_search, ask_video_or_playlist


_PREP_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=4)
_PREP_FUT = {}
_PREP_DONE = {}
_PREP_MAX = 200
_PREFETCH_N = 5


def _opts(ctx, ses=None):
    if isinstance(ses, dict):
        return {
            "audio_only": bool(ses.get("audio_only", True)),
            "quality": str(ses.get("quality", "medium") or "medium"),
        }
    if ctx is None:
        return {"audio_only": True, "quality": "medium"}
    return {
        "audio_only": bool(ctx.settings.get_yt_audio_only()),
        "quality": str(ctx.settings.get_yt_video_quality() or "medium"),
    }


def _prep_key(url, opts):
    src = str(url or "").strip()
    audio_only = "1" if bool(opts.get("audio_only")) else "0"
    quality = str(opts.get("quality", "medium") or "medium").strip().lower()
    return f"{src}|a={audio_only}|q={quality}"


def open_yt(ctx):
    if ctx.frame is None:
        return
    if not has_all():
        _show_error(ctx, _("YouTube components are missing."), _("Error"))
        return

    link = ask_link(ctx.frame)
    if not link:
        return
    open_yt_link(ctx, link)


def open_yt_link(ctx, link, forced_kind=""):
    if ctx.frame is None:
        return False
    if not has_all():
        _show_error(ctx, _("YouTube components are missing."), _("Error"))
        return False

    info = parse_link(link)
    if not info.is_http:
        _show_error(ctx, _("The link must start with http or https."), _("Invalid link"))
        return False
    if not info.is_youtube:
        _show_error(ctx, _("This is not a valid YouTube link."), _("Invalid YouTube link"))
        return False

    kind = str(info.kind or "")
    pref = str(forced_kind or "").strip().lower()
    if pref == "video":
        if not bool(info.has_video):
            _show_error(
                ctx,
                _("This link does not include a YouTube video."),
                _("Invalid YouTube link"),
            )
            return False
        kind = "video"
    elif pref == "playlist":
        if not bool(info.has_playlist):
            _show_error(
                ctx,
                _("This link does not include a YouTube playlist."),
                _("Invalid YouTube link"),
            )
            return False
        kind = "playlist"
    elif bool(info.has_video) and bool(info.has_playlist):
        mode = str(ctx.settings.get_yt_mixed_link_mode() or "ask").strip().lower()
        if mode == "playlist":
            kind = "playlist"
        elif mode == "video":
            kind = "video"
        else:
            choice = ask_video_or_playlist(ctx.frame)
            if choice == "playlist":
                kind = "playlist"
            elif choice == "video":
                kind = "video"
            else:
                return False

    if kind == "channel":
        _show_error(
            ctx,
            _("Channel links are not supported here."),
            _("Invalid YouTube link"),
        )
        return False
    if kind == "playlist":
        res = _inspect(ctx, info.raw)
        if res is None:
            return False
        ses = mk_ses("playlist", str(res.title or ""), list(res.items or []))
        ses.update(_opts(ctx))
        show_res(
            ctx,
            ses,
            sel=0,
            prefetch=_prefetch_range,
            play_item=_play_item,
            pool=_PREP_POOL,
            prefetch_n=_PREFETCH_N,
        )
        return True
    if kind != "video":
        _show_error(ctx, _("This is not a valid YouTube link."), _("Invalid YouTube link"))
        return False

    _clear_ctx_ses(ctx)
    item = YtItem(
        title=str(info.raw),
        url=str(info.raw),
        channel_url="",
        channel_name="",
        description="",
    )
    return bool(_play_item(ctx, item, ses=None, idx=None))


def search_yt(ctx):
    if ctx.frame is None:
        return
    if not has_all():
        ctx.speak(_("YouTube components are missing."), _("Missing components."))
        return

    query = ask_search(ctx.frame)
    if not query:
        return

    ses_opts = _opts(ctx)
    out = _search(ctx, query, ses_opts)
    if out is None:
        return

    ses = mk_ses(
        "search",
        _("Search results: {query}").format(query=query),
        list(out["items"] or []),
        search=out["search"],
    )
    ses.update(ses_opts)
    first = out.get("first")
    if isinstance(first, dict):
        first_item = first.get("item")
        first_url = str(getattr(first_item, "url", "") or "")
        if not first_url and ses["items"]:
            first_url = str(ses["items"][0].url or "")
        if first_url:
            _cache_set(_prep_key(first_url, ses_opts), first)
    show_res(
        ctx,
        ses,
        sel=0,
        prefetch=_prefetch_range,
        play_item=_play_item,
        pool=_PREP_POOL,
        prefetch_n=_PREFETCH_N,
    )


def on_esc(ctx):
    ses = get_ses(ctx)
    if ses is None or ctx.frame is None:
        return False

    src = str(ctx.player.current_source or "").strip()
    if not src or src not in ses["urls"]:
        return False

    # Returning to the results window should stop playback fully.
    ctx.player.stop()
    ctx.player.remove_sources(ses.get("urls", []))
    ctx.set_playing(False)
    ctx.set_file_loaded(False)
    show_res(
        ctx,
        ses,
        sel=ses["sel"],
        prefetch=_prefetch_range,
        play_item=_play_item,
        pool=_PREP_POOL,
        prefetch_n=_PREFETCH_N,
    )
    return True


def try_next(ctx):
    ses = get_ses(ctx)
    if ses is None:
        return None

    cur_idx = ses_idx(ctx, ses)
    if cur_idx is None:
        return None
    ses["sel"] = cur_idx
    nxt = cur_idx + 1
    if nxt < 0 or nxt >= len(ses.get("items", [])):
        ses["pending_next"] = None
        return False

    item = ses["items"][nxt]
    key = _prep_key(item.url, _opts(ctx, ses))
    ses["pending_next"] = {"from": cur_idx, "to": nxt, "key": key}
    prep = _cache_get(key)
    if isinstance(prep, dict):
        moved = _advance_to_next(ctx, ses, cur_idx, nxt, item, prep)
        if moved:
            ses["pending_next"] = None
        return moved

    _load_next_bg(ctx, ses, item, cur_idx, nxt)
    return False


def sync_sel(ctx):
    ses = get_ses(ctx)
    if ses is None:
        return False
    cur_idx = ses_idx(ctx, ses)
    if cur_idx is None:
        return False
    ses["sel"] = cur_idx
    item = ses["items"][cur_idx]
    set_now(ctx, item)
    return True


def _search(ctx, query, ses_opts):
    add_to_path()

    def job(cancel, on_line, _on_up):
        on_line(_("Searching videos..."))
        state = start_search(query, limit=50, language="en", region="US")
        items = list(getattr(state, "items", []) or [])
        if not items:
            raise ResolveError(_("No videos were found for this search."))

        on_line(_("Fetching first stream..."))
        first = None
        try:
            first = fetch_play(
                items[0].url,
                cancel,
                on_line=on_line,
                audio_only=ses_opts.get("audio_only", True),
                quality=ses_opts.get("quality", "medium"),
            )
        except Exception:
            first = None
        return {"search": state, "items": items, "first": first}

    out = run_task(
        ctx.frame,
        _("Searching YouTube"),
        job,
        simple=True,
    )
    if out.can:
        return None
    if not out.ok:
        err = out.err or _("Could not complete YouTube search.")
        _show_error(ctx, err, _("YouTube"))
        return None
    return out.val


def _inspect(ctx, link):
    add_to_path()

    def job(cancel, on_line, _on_up):
        return inspect_link(link, cancel, on_line=on_line)

    out = run_task(
        ctx.frame,
        _("Loading YouTube link"),
        job,
        simple=True,
    )
    if out.can:
        return None
    if not out.ok:
        err = out.err or _("Could not read YouTube link data.")
        _show_error(ctx, err, _("YouTube"))
        return None
    return out.val


def _play_item(ctx, item, ses, idx):
    prep = _prep_play(ctx, item, _opts(ctx, ses))
    if prep is None:
        return False

    item = prep["item"]
    stream = prep["stream"]
    src = str(item.url or "").strip()
    ttl = str(item.title or "").strip()

    add_to_path()
    # Keep YouTube/session playback deterministic and aligned with result order.
    ctx.player.set_shuffle_enabled(False)
    if ctx.frame is not None:
        try:
            ctx.frame.set_shuffle_checked(False)
        except Exception:
            pass
    ok = ctx.player.open_stream(
        stream,
        append=True,
        title=ttl,
        source_url=src,
    )
    if not ok:
        _show_error(ctx, _("Could not open YouTube stream."), _("Error"))
        return False

    ctx.reset_selection()
    ctx.set_file_loaded(True)
    ctx.set_playing(True)
    set_now(ctx, item)

    if ses is None:
        _clear_ctx_ses(ctx)
    else:
        set_ses(ctx, ses, idx)
        _mark_queued(ses, src)
        _prefetch_range(ses, int(idx or 0) + 1, 1)
    return True


def _prep_play(ctx, item, ses_opts):
    key = _prep_key(getattr(item, "url", ""), ses_opts)
    if key:
        cached = _cache_get(key)
        if cached is not None:
            return cached
        fut = _PREP_FUT.get(key)
        if fut is not None and fut.done():
            try:
                ready = fut.result()
            except Exception:
                ready = None
            _PREP_FUT.pop(key, None)
            if isinstance(ready, dict):
                _cache_set(key, ready)
                return ready

    add_to_path()

    def job(cancel, on_line, _on_up):
        if key and key in _PREP_FUT:
            fut = _PREP_FUT[key]
            while True:
                if cancel.is_set():
                    raise CancelledError()
                try:
                    ready = fut.result(timeout=0.1)
                    if isinstance(ready, dict):
                        return ready
                    break
                except concurrent.futures.TimeoutError:
                    continue
                except Exception:
                    break
        return fetch_play(
            item.url,
            cancel,
            on_line=on_line,
            audio_only=ses_opts.get("audio_only", True),
            quality=ses_opts.get("quality", "medium"),
        )

    out = run_task(
        ctx.frame,
        _("Loading YouTube stream"),
        job,
        simple=True,
    )
    if out.can:
        return None
    if not out.ok:
        err = out.err or _("Could not resolve YouTube stream.")
        _show_error(ctx, err, _("YouTube"))
        return None
    if key and isinstance(out.val, dict):
        _cache_set(key, out.val)
    return out.val


def _prefetch_range(ses, start, count):
    items = list(ses.get("items", []))
    if not items or count <= 0:
        return
    ses_opts = _opts(None, ses)
    pos = max(0, int(start))
    end = min(len(items), pos + int(count))
    for idx in range(pos, end):
        _prefetch_one(ses, items[idx], ses_opts)


def _prefetch_one(ses, item, ses_opts):
    key = _prep_key(getattr(item, "url", ""), ses_opts)
    if not key:
        return
    if _cache_get(key) is not None:
        return
    fut = _PREP_FUT.get(key)
    if fut is not None and not fut.done():
        return
    ses.setdefault("prep_keys", set()).add(key)
    prep_jobs = ses.setdefault("prep_jobs", {})
    old = prep_jobs.get(key)
    if old is not None and not old.done():
        return
    cancel = ses.get("cancel")
    if cancel is None:
        cancel = CancelFlag()
        ses["cancel"] = cancel

    def job():
        try:
            return fetch_play(
                item.url,
                cancel,
                audio_only=ses_opts.get("audio_only", True),
                quality=ses_opts.get("quality", "medium"),
            )
        except Exception:
            return None

    future = _PREP_POOL.submit(job)
    _PREP_FUT[key] = future
    prep_jobs[key] = future

    def done(_future):
        prep_jobs.pop(key, None)
        _PREP_FUT.pop(key, None)
        try:
            ready = _future.result()
        except Exception:
            ready = None
        if isinstance(ready, dict):
            _cache_set(key, ready)

    future.add_done_callback(done)


def _load_next_bg(ctx, ses, item, from_idx, to_idx):
    ses_opts = _opts(ctx, ses)
    key = _prep_key(getattr(item, "url", ""), ses_opts)
    if not key:
        return
    ses.setdefault("prep_keys", set()).add(key)
    cancel = ses.get("cancel")
    if cancel is None:
        cancel = CancelFlag()
        ses["cancel"] = cancel
    jobs = ses.setdefault("next_jobs", {})
    old = jobs.get(key)
    if old is not None and not old.done():
        return

    ctx.speak(_("Loading next video..."), _("Loading next video..."))

    def job():
        try:
            return fetch_play(
                item.url,
                cancel,
                audio_only=ses_opts.get("audio_only", True),
                quality=ses_opts.get("quality", "medium"),
            )
        except Exception:
            return None

    fut = _PREP_POOL.submit(job)
    jobs[key] = fut

    def done(_future):
        try:
            prep = _future.result()
        except Exception:
            prep = None
        if not isinstance(prep, dict):
            return
        _cache_set(key, prep)
        wx.CallAfter(_queue_next_ready, ctx, ses, item, prep, from_idx, to_idx, key)

    fut.add_done_callback(done)


def _queue_next_ready(ctx, ses, item, prep, from_idx, to_idx, key):
    cur = get_ses(ctx)
    if cur is None or cur is not ses:
        return
    _ensure_queued(ctx, ses, item, prep)
    _auto_next_if_pending(ctx, ses, from_idx, to_idx, key, item, prep)


def _auto_next_if_pending(ctx, ses, from_idx, to_idx, key, item, prep):
    pending = ses.get("pending_next")
    if not isinstance(pending, dict):
        return
    if str(pending.get("key") or "") != str(key or ""):
        return
    cur_idx = ses_idx(ctx, ses)
    if cur_idx is None:
        return
    if int(cur_idx) != int(from_idx):
        return
    if _advance_to_next(ctx, ses, from_idx, to_idx, item, prep):
        ses["pending_next"] = None


def _advance_to_next(ctx, ses, from_idx, to_idx, item, prep):
    if not _ensure_queued(ctx, ses, item, prep):
        return False
    cur_idx = ses_idx(ctx, ses)
    if cur_idx is None or int(cur_idx) != int(from_idx):
        return False
    moved = bool(ctx.player.next_track())
    if not moved:
        return False
    ses["sel"] = int(to_idx)
    set_now(ctx, item)
    _prefetch_range(ses, int(to_idx) + 1, 1)
    return True


def _ensure_queued(ctx, ses, item, prep):
    key = str(getattr(item, "url", "") or "").strip()
    if not key:
        return False
    if _is_queued(ses, key):
        return True
    stream = str(prep.get("stream") or "").strip()
    if not stream:
        return False
    title = str(getattr(item, "title", "") or "")
    if not ctx.player.queue_stream(stream, title=title, source_url=key):
        return False
    _mark_queued(ses, key)
    return True


def _is_queued(ses, key):
    return key in ses.setdefault("queued", set())


def _mark_queued(ses, key):
    ses.setdefault("queued", set()).add(str(key or ""))


def _cache_get(key):
    value = _PREP_DONE.get(key)
    if isinstance(value, dict):
        return value
    fut = _PREP_FUT.get(key)
    if fut is None or not fut.done():
        return None
    try:
        value = fut.result()
    except Exception:
        value = None
    _PREP_FUT.pop(key, None)
    if isinstance(value, dict):
        _cache_set(key, value)
        return value
    return None


def _cache_set(key, value):
    _PREP_DONE[key] = value
    while len(_PREP_DONE) > _PREP_MAX:
        first = next(iter(_PREP_DONE))
        _PREP_DONE.pop(first, None)


def _clear_ctx_ses(ctx):
    ses = get_ses(ctx)
    keys = set()
    if isinstance(ses, dict):
        keys = set(ses.get("prep_keys", set()) or set())
    clear_ses(ctx)
    for key in keys:
        fut = _PREP_FUT.pop(key, None)
        if fut is not None and not fut.done():
            try:
                fut.cancel()
            except Exception:
                pass


def _show_error(ctx, message, title):
    if ctx.frame is None:
        return
    wx.MessageBox(
        str(message or ""),
        str(title or _("Error")),
        wx.OK | wx.ICON_ERROR,
        parent=ctx.frame,
    )

