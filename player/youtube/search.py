import asyncio
from dataclasses import dataclass, field

from py_yt import VideosSearch

from .resolver import YtItem


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
    search = VideosSearch(text, limit=int(limit), language=language, region=region)
    data = _run(search.next())
    items = _to_items(data)
    cont = str(getattr(search, "continuationKey", "") or "")
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
    search = VideosSearch(
        state.query,
        limit=int(state.limit),
        language=state.language,
        region=state.region,
    )
    if cancel is not None and cancel.is_set():
        return []
    search.continuationKey = state.cont
    data = _run(search.next())
    if cancel is not None and cancel.is_set():
        return []
    items = _to_items(data)
    if cancel is not None and cancel.is_set():
        return []
    state.items.extend(items)
    state.cont = str(getattr(search, "continuationKey", "") or "")
    return items


def _run(awaitable, timeout=20):
    async def _with_timeout():
        return await asyncio.wait_for(awaitable, timeout=float(timeout))

    try:
        return asyncio.run(_with_timeout())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_with_timeout())
        finally:
            loop.close()


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
