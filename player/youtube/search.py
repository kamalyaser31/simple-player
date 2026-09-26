import asyncio
import threading
from dataclasses import dataclass, field

from py_yt import VideosSearch
from py_yt.handlers.componenthandler import ComponentHandler

from .resolver import YtItem

# Guard against py_yt TypeError when a shelf has no verticalListRenderer elements
_orig_get_shelf = getattr(ComponentHandler, "_getShelfComponent", None)
if _orig_get_shelf is not None:

    def _safe_get_shelf(self, element):
        res = _orig_get_shelf(self, element)
        if isinstance(res, dict) and not isinstance(res.get("elements"), list):
            res["elements"] = []
        return res

    ComponentHandler._getShelfComponent = _safe_get_shelf


@dataclass
class SearchState:
    query: str
    limit: int = 50
    language: str = "en"
    region: str = "US"
    cont: str = ""
    items: list = field(default_factory=list)

    def has_more(self):
        return bool(self.cont)


def start_search(query, limit=50, language="en", region="US"):
    text = str(query or "").strip()
    data, cont = _run_search_sync(
        lambda: VideosSearch(text, limit=int(limit), language=language, region=region)
    )
    items = _to_items(data)
    return SearchState(
        query=text,
        limit=int(limit),
        language=str(language or "en"),
        region=str(region or "US"),
        cont=cont,
        items=items,
    )


def load_more(state, cancel=None):
    if state is None or not state.has_more():
        return []
    if cancel is not None and cancel.is_set():
        return []

    def make_search():
        s = VideosSearch(
            state.query,
            limit=int(state.limit),
            language=state.language,
            region=state.region,
        )
        s.continuationKey = state.cont
        return s

    if cancel is not None and cancel.is_set():
        return []

    try:
        data, cont = _run_search_sync(make_search)
    except Exception:
        return []

    if cancel is not None and cancel.is_set():
        return []
    items = _to_items(data)
    if cancel is not None and cancel.is_set():
        return []
    state.items.extend(items)
    state.cont = cont
    return items


def _run_search_sync(search_factory, timeout=20.0):
    result = None
    exception = None

    def worker():
        nonlocal result, exception
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        search = None
        try:
            search = search_factory()
            coro = asyncio.wait_for(search.next(), timeout=float(timeout))
            data = loop.run_until_complete(coro)
            cont = str(getattr(search, "continuationKey", "") or "")
            result = (data, cont)
        except Exception as exc:
            exception = exc
        finally:
            if (
                search is not None
                and hasattr(search, "async_client")
                and search.async_client is not None
            ):
                try:
                    loop.run_until_complete(search.async_client.aclose())
                except Exception:
                    pass
            try:
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                if pending:
                    loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )
                loop.run_until_complete(loop.shutdown_asyncgens())
            except Exception:
                pass
            loop.close()
            asyncio.set_event_loop(None)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    thread.join(timeout=float(timeout) + 5.0)
    if thread.is_alive():
        raise TimeoutError("YouTube search timed out.")
    if exception is not None:
        raise exception
    return result


def _run(awaitable, timeout=20):
    async def _with_timeout():
        return await asyncio.wait_for(awaitable, timeout=float(timeout))

    return asyncio.run(_with_timeout())


def _to_items(data):
    out = []
    if not isinstance(data, dict):
        return out
    for entry in data.get("result", []) or []:
        if not isinstance(entry, dict):
            continue
        item = _to_item(entry)
        if item is not None:
            out.append(item)
    return out


def _to_item(entry):
    url = str(entry.get("link") or "").strip()
    vid = str(entry.get("id") or "").strip()
    if not url and vid:
        url = f"https://www.youtube.com/watch?v={vid}"
    if not url:
        return None

    title = str(entry.get("title") or "").strip() or url
    channel = entry.get("channel") or {}
    if not isinstance(channel, dict):
        channel = {}
    channel_name = str(channel.get("name") or "").strip()
    channel_url = str(channel.get("link") or "").strip()
    desc = _desc(entry.get("descriptionSnippet"))
    return YtItem(
        title=title,
        url=url,
        channel_url=channel_url,
        channel_name=channel_name,
        description=desc,
    )


def _desc(parts):
    if not isinstance(parts, list):
        return ""
    out = []
    for part in parts:
        if isinstance(part, dict):
            text = str(part.get("text") or "").strip()
            if text:
                out.append(text)
    return " ".join(out)
