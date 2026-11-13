import os
import time
from dataclasses import dataclass

from helpers.json_store import read_json, write_json

SUB_KINDS = ("channel", "playlist")
CHANNEL_URL = "https://www.youtube.com/channel/"
PLAYLIST_URL = "https://www.youtube.com/playlist?list="


@dataclass
class Sub:
    id: str
    kind: str
    name: str
    url: str
    added: float


def sub_from_dict(data):
    if not isinstance(data, dict):
        return None
    sub_id = str(data.get("id") or "").strip()
    kind = str(data.get("kind") or "").strip().lower()
    name = str(data.get("name") or "").strip()
    url = str(data.get("url") or "").strip()
    if not sub_id or not name or not url or kind not in SUB_KINDS:
        return None
    try:
        added = float(data.get("added") or 0.0)
    except (TypeError, ValueError):
        added = 0.0
    return Sub(id=sub_id, kind=kind, name=name, url=url, added=added)


def sub_to_dict(sub):
    return {
        "id": sub.id,
        "kind": sub.kind,
        "name": sub.name,
        "url": sub.url,
        "added": sub.added,
    }


class SubStore:
    def __init__(self, settings_path, filename="subscriptions.json"):
        settings_file = str(settings_path or "").strip()
        root = os.path.dirname(settings_file) if settings_file else ""
        self._path = os.path.join(root, filename) if root else filename

    @property
    def path(self):
        return self._path

    def list_all(self):
        """Return all subscriptions, newest first."""
        out = []
        for row in self._rows():
            sub = sub_from_dict(row)
            if sub is not None:
                out.append(sub)
        out.reverse()
        out.sort(key=lambda sub: sub.added, reverse=True)
        return out

    def channels(self):
        return [sub for sub in self.list_all() if sub.kind == "channel"]

    def has(self, kind, ident):
        target = str(ident or "").strip()
        return any(sub.kind == kind and sub.id == target for sub in self.list_all())

    def add(self, kind, ident, name):
        """Add a subscription; return None when it already exists."""
        kind = str(kind or "").strip().lower()
        ident = str(ident or "").strip()
        if kind not in SUB_KINDS or not ident:
            raise ValueError("Invalid subscription.")
        if self.has(kind, ident):
            return None
        prefix = CHANNEL_URL if kind == "channel" else PLAYLIST_URL
        sub = Sub(
            id=ident,
            kind=kind,
            name=str(name or "").strip() or ident,
            url=prefix + ident,
            added=time.time(),
        )
        rows = self._rows()
        rows.append(sub_to_dict(sub))
        write_json(self._path, {"version": 1, "items": rows})
        return sub

    def delete(self, sub_id):
        target = str(sub_id or "").strip()
        rows = self._rows()
        kept = [row for row in rows if str(row.get("id") or "").strip() != target]
        if not target or len(kept) == len(rows):
            return False
        write_json(self._path, {"version": 1, "items": kept})
        return True

    def _rows(self):
        rows = read_json(self._path).get("items")
        if not isinstance(rows, list):
            return []
        return [row for row in rows if isinstance(row, dict)]
