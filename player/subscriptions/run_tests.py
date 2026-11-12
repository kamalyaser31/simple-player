"""Small manual tests for the subscriptions package.

Run from the player folder:
    python subscriptions/run_tests.py          offline tests
    python subscriptions/run_tests.py --live   also hit YouTube once
"""

import argparse
import os
import sys
import tempfile
import time
import traceback
from gettext import gettext as _

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from subscriptions.feed import (  # noqa: E402
    age_label,
    channel_id_from_html,
    feed_row,
    fetch_feed,
    merge_latest,
    parse_feed,
    parse_link,
    resolve_link,
)
from subscriptions.store import SubStore  # noqa: E402
from youtube.resolver import YtItem  # noqa: E402

WATCH_NEW = "https://www.youtube.com/watch?v=newvideo0001"
WATCH_OLD = "https://www.youtube.com/watch?v=oldvideo0001"
SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015"
      xmlns="http://www.w3.org/2005/Atom">
 <title>Sample Channel</title>
 <entry>
  <yt:videoId>newvideo0001</yt:videoId>
  <title>New video</title>
  <link rel="alternate" href="https://www.youtube.com/watch?v=newvideo0001"/>
  <author><name>Sample Channel</name>
   <uri>https://www.youtube.com/channel/UCabcdefghijklmnopqrstuv</uri></author>
  <published>2026-11-01T10:00:00+00:00</published>
 </entry>
 <entry>
  <yt:videoId>shortvideo01</yt:videoId>
  <title>A short</title>
  <link rel="alternate" href="https://www.youtube.com/shorts/shortvideo01"/>
  <author><name>Sample Channel</name>
   <uri>https://www.youtube.com/channel/UCabcdefghijklmnopqrstuv</uri></author>
  <published>2026-10-15T10:00:00+00:00</published>
 </entry>
 <entry>
  <yt:videoId>oldvideo0001</yt:videoId>
  <title>Old video</title>
  <link rel="alternate" href="https://www.youtube.com/watch?v=oldvideo0001"/>
  <author><name>Sample Channel</name>
   <uri>https://www.youtube.com/channel/UCabcdefghijklmnopqrstuv</uri></author>
  <published>2026-10-01T10:00:00+00:00</published>
 </entry>
</feed>
"""


def test_parse_feed_drops_shorts():
    title, items = parse_feed(SAMPLE)
    assert title == "Sample Channel"
    assert [i.url for i in items] == [WATCH_NEW, WATCH_OLD]
    assert items[0].channel_name == "Sample Channel"
    assert items[0].channel_url.endswith("UCabcdefghijklmnopqrstuv")
    assert items[0].published > items[1].published


def test_parse_feed_invalid_xml():
    try:
        parse_feed("<feed")
    except ValueError:
        return
    raise AssertionError("ValueError expected")


def test_parse_link():
    chan = "UC_x5XG1OV2P6uZZ5FSM9Ttw"
    assert parse_link(f"https://www.youtube.com/channel/{chan}") == ("channel", chan)
    assert parse_link("https://youtube.com/playlist?list=PLabc123") == (
        "playlist",
        "PLabc123",
    )
    assert parse_link("https://www.youtube.com/watch?v=x&list=PLabc123") == (
        "playlist",
        "PLabc123",
    )
    assert parse_link("https://www.youtube.com/@SomeName")[0] == "channel_page"
    assert parse_link("https://www.youtube.com/c/Some")[0] == "channel_page"
    assert parse_link("https://www.youtube.com/user/Some")[0] == "channel_page"
    assert parse_link("https://example.com/x") == ("", "")
    assert parse_link("https://www.youtube.com/watch?v=x") == ("", "")
    assert parse_link("") == ("", "")


def test_channel_id_from_html():
    cid = "UCabcdefghijklmnopqrstuv"
    html = f'<link rel="canonical" href="https://www.youtube.com/channel/{cid}">'
    assert channel_id_from_html(html) == cid
    assert channel_id_from_html(f'"externalId":"{cid}"') == cid
    assert channel_id_from_html("<html></html>") == ""


def _feed_of(count, offset):
    return [
        YtItem("t", f"https://x/{offset}-{n}", "", "c", published=float(offset + n))
        for n in range(count)
    ]


def test_merge_latest_sorts_and_limits():
    feeds = [_feed_of(20, 0), _feed_of(20, 5), _feed_of(20, 11)]
    out = merge_latest(feeds, limit=50)
    assert len(out) == 50
    assert all(a.published >= b.published for a, b in zip(out, out[1:]))
    dup = YtItem("t", "https://x/dup", "", "c", published=1.0)
    assert len(merge_latest([[dup], [dup]])) == 1


def test_age_label():
    now = time.time()
    assert age_label(now - 3600, now) == _("today")
    assert age_label(now - 86400 * 1.5, now) == _("yesterday")
    assert age_label(now - 86400 * 5, now) == _("{n} days ago").format(n=5)
    assert age_label(now - 86400 * 70, now) == _("{n} months ago").format(n=2)
    assert age_label(now - 86400 * 800, now) == _("{n} years ago").format(n=2)


def test_feed_row():
    now = time.time()
    item = YtItem("Title", "u", "", "Chan", published=now - 86400 * 5)
    age = _("{n} days ago").format(n=5)
    assert feed_row(item, "feed", now) == f"Title - Chan - {age}"
    assert feed_row(item, "channel", now) == f"Title - {age}"
    assert feed_row(item, "search", now) == "Title"


def test_store_add_dedupe_order_delete():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "settings.json")
        st = SubStore(path)
        assert st.list_all() == []
        st.add("channel", "UCaaa", "A")
        st.add("playlist", "PLbbb", "B")
        assert st.add("channel", "UCaaa", "A again") is None
        assert [s.id for s in SubStore(path).list_all()] == ["PLbbb", "UCaaa"]
        assert [s.id for s in st.channels()] == ["UCaaa"]
        assert st.list_all()[1].url == "https://www.youtube.com/channel/UCaaa"
        assert st.delete("UCaaa") and not st.has("channel", "UCaaa")
        assert not st.delete("UCaaa")


def test_store_corrupt_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "settings.json")
        with open(os.path.join(tmp, "subscriptions.json"), "w") as handle:
            handle.write("{not json")
        st = SubStore(path)
        assert st.list_all() == []
        assert st.add("channel", "UCaaa", "A") is not None


def test_store_ignores_bad_rows():
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "subscriptions.json"), "w") as handle:
            handle.write(
                '{"version": 1, "items": [{"id": "x"}, 5, '
                '{"id": "a", "kind": "bogus", "name": "n", "url": "u"}]}'
            )
        assert SubStore(os.path.join(tmp, "settings.json")).list_all() == []


def run_live():
    title, items = fetch_feed("channel", "UC_x5XG1OV2P6uZZ5FSM9Ttw")
    print(f"live feed: {title!r}, {len(items)} items")
    assert items
    kind, ident, name = resolve_link("https://www.youtube.com/@GoogleDevelopers")
    print(f"live resolve: {kind} {ident} {name!r}")
    assert kind == "channel" and ident.startswith("UC")


def main():
    parser = argparse.ArgumentParser(description="Subscriptions tests.")
    parser.add_argument("--live", action="store_true", help="also hit YouTube")
    args = parser.parse_args()
    tests = [
        (name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_")
    ]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except Exception:
            failed += 1
            print(f"FAIL {name}", file=sys.stderr)
            traceback.print_exc()
    if args.live:
        try:
            run_live()
            print("PASS live")
        except Exception:
            failed += 1
            print("FAIL live", file=sys.stderr)
            traceback.print_exc()
    print(f"{len(tests) - min(failed, len(tests))}/{len(tests)} offline passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
