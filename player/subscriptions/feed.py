import datetime
import re
import urllib.request
import xml.etree.ElementTree as ET
from gettext import gettext as _
from urllib.parse import parse_qs, quote, urlparse

from youtube.resolver import YtItem

ATOM = "{http://www.w3.org/2005/Atom}"
YT = "{http://www.youtube.com/xml/schemas/2015}"
FEED_URL = "https://www.youtube.com/feeds/videos.xml"
WATCH_URL = "https://www.youtube.com/watch?v="
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
# Without this cookie the European consent page replaces the channel page.
CONSENT_COOKIE = "CONSENT=YES+1"

_CHANNEL_ID = r"UC[\w-]{22}"
_CHANNEL_PATH = re.compile(r"^/channel/(" + _CHANNEL_ID + ")")
_PAGE_PATH = re.compile(r"^/(@|c/|user/)[^/]+")
_CANONICAL = re.compile(
    r"""rel=["']canonical["'][^>]*href=["'][^"']*/channel/(""" + _CHANNEL_ID + ")"
)
_EXTERNAL_ID = re.compile(r'"externalId"\s*:\s*"(' + _CHANNEL_ID + ')"')


def parse_link(link):
    """Classify a YouTube link as channel, playlist, channel page, or neither."""
    text = str(link or "").strip()
    if not text:
        return ("", "")
    if "//" not in text:
        text = "https://" + text
    try:
        parts = urlparse(text)
    except ValueError:
        return ("", "")
    host = (parts.hostname or "").lower()
    if not (host == "youtube.com" or host.endswith(".youtube.com")):
        return ("", "")
    query = parse_qs(parts.query)
    path = parts.path or ""

    playlist_id = (query.get("list") or [""])[0].strip()
    if playlist_id:
        return ("playlist", playlist_id)
    match = _CHANNEL_PATH.match(path)
    if match:
        return ("channel", match.group(1))
    channel_id = (query.get("channel_id") or [""])[0].strip()
    if channel_id:
        return ("channel", channel_id)
    if _PAGE_PATH.match(path):
        return ("channel_page", text)
    return ("", "")


def channel_id_from_html(html):
    text = str(html or "")
    for pattern in (_CANONICAL, _EXTERNAL_ID):
        match = pattern.search(text)
        if match:
            return match.group(1)
    return ""


def parse_feed(xml_text):
    """Return (feed title, items); Shorts are dropped."""
    data = xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise ValueError(str(exc)) from exc
    title = (root.findtext(ATOM + "title") or "").strip()
    items = []
    for entry in root.findall(ATOM + "entry"):
        item = _entry_item(entry, title)
        if item is not None:
            items.append(item)
    return title, items


def _entry_item(entry, feed_title):
    video_id = (entry.findtext(YT + "videoId") or "").strip()
    if not video_id:
        return None
    for link in entry.findall(ATOM + "link"):
        if "/shorts/" in str(link.get("href") or ""):
            return None
    author = entry.find(ATOM + "author")
    name = ""
    uri = ""
    if author is not None:
        name = (author.findtext(ATOM + "name") or "").strip()
        uri = (author.findtext(ATOM + "uri") or "").strip()
    return YtItem(
        title=(entry.findtext(ATOM + "title") or "").strip() or video_id,
        url=WATCH_URL + video_id,
        channel_url=uri,
        channel_name=name or feed_title,
        description="",
        published=_timestamp(entry.findtext(ATOM + "published")),
    )


def _timestamp(text):
    value = str(text or "").strip()
    if not value:
        return 0.0
    try:
        stamp = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return 0.0
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=datetime.timezone.utc)
    return stamp.timestamp()


def _http_get(url, timeout):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Cookie": CONSENT_COOKIE},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_feed(kind, ident, timeout=15):
    if kind == "channel":
        url = FEED_URL + "?channel_id=" + quote(str(ident), safe="")
    elif kind == "playlist":
        url = FEED_URL + "?playlist_id=" + quote(str(ident), safe="")
    else:
        raise ValueError(_("This is not a valid YouTube channel or playlist link."))
    return parse_feed(_http_get(url, timeout))


def resolve_link(link, timeout=15):
    """Return (kind, id, name) for a channel or playlist link."""
    kind, ident = parse_link(link)
    if not kind:
        raise ValueError(_("This is not a valid YouTube channel or playlist link."))
    if kind == "channel_page":
        ident = channel_id_from_html(_http_get(ident, timeout))
        if not ident:
            raise ValueError(_("Could not find the channel for this link."))
        kind = "channel"
    title, _items = fetch_feed(kind, ident, timeout)
    return kind, ident, title or ident


def merge_latest(feeds, limit=50):
    seen = set()
    merged = []
    for items in feeds:
        for item in items:
            if item.url in seen:
                continue
            seen.add(item.url)
            merged.append(item)
    merged.sort(key=lambda item: item.published, reverse=True)
    return merged[:limit]


def age_label(published, now):
    days = int((now - published) // 86400)
    if days <= 0:
        return _("today")
    if days == 1:
        return _("yesterday")
    if days <= 30:
        return _("{n} days ago").format(n=days)
    if days < 365:
        return _("{n} months ago").format(n=min(11, days // 30))
    return _("{n} years ago").format(n=days // 365)


def feed_row(item, kind, now):
    """Build the list line of a result item for the given session kind."""
    if kind not in ("feed", "channel"):
        return item.title
    parts = [item.title]
    if kind == "feed" and item.channel_name:
        parts.append(item.channel_name)
    if item.published > 0:
        parts.append(age_label(item.published, now))
    return " - ".join(parts)
