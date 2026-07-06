import os
import time
import uuid

from .fileio import read_json, write_json
from .model import FAV_TYPES, Fav, fav_from_dict, fav_to_dict


class FavStore:
    def __init__(self, settings_path, filename="favorites.json"):
        settings_file = str(settings_path or "").strip()
        root = os.path.dirname(settings_file) if settings_file else ""
        self._path = os.path.join(root, filename) if root else filename

    @property
    def path(self):
        return self._path

    def list_all(self):
        packet = self._load()
        rows = packet.get("items")
        if not isinstance(rows, list):
            return []
        out = []
        for row in rows:
            item = fav_from_dict(row)
            if item is None:
                continue
            out.append(item)
        return self._sort(out)

    def get(self, fav_id):
        target = str(fav_id or "").strip()
        if not target:
            return None
        for item in self.list_all():
            if str(item.id or "").strip() == target:
                return item
        return None

    def add(self, name, kind, link):
        item = Fav(
            id=uuid.uuid4().hex,
            name=self._name(name),
            kind=self._kind(kind),
            link=self._link(link),
            created=time.time(),
        )
        self._validate(item)
        packet = self._load()
        rows = packet.get("items")
        if not isinstance(rows, list):
            rows = []
        rows.append(fav_to_dict(item))
        packet["items"] = rows
        self._save(packet)
        return item

    def update(self, fav_id, name, kind, link):
        target = str(fav_id or "").strip()
        if not target:
            return False
        packet = self._load()
        rows = packet.get("items")
        if not isinstance(rows, list):
            rows = []
        changed = False
        for row in rows:
            if str(row.get("id") or "").strip() != target:
                continue
            row["name"] = self._name(name)
            row["kind"] = self._kind(kind)
            row["link"] = self._link(link)
            test = fav_from_dict(row)
            self._validate(test)
            changed = True
            break
        if not changed:
            return False
        packet["items"] = rows
        self._save(packet)
        return True

    def delete(self, fav_id):
        target = str(fav_id or "").strip()
        if not target:
            return False
        packet = self._load()
        rows = packet.get("items")
        if not isinstance(rows, list):
            return False
        kept = [row for row in rows if str(row.get("id") or "").strip() != target]
        if len(kept) == len(rows):
            return False
        packet["items"] = kept
        self._save(packet)
        return True

    def _validate(self, item):
        if item is None:
            raise ValueError("Invalid favorite item.")
        if not str(item.name or "").strip():
            raise ValueError("Favorite name is required.")
        if str(item.kind or "").strip().lower() not in FAV_TYPES:
            raise ValueError("Invalid favorite type.")
        if not str(item.link or "").strip():
            raise ValueError("Favorite link is required.")

    def _load(self):
        packet = read_json(self._path)
        if not isinstance(packet, dict):
            packet = {}
        if "version" not in packet:
            packet["version"] = 1
        if not isinstance(packet.get("items"), list):
            packet["items"] = []
        return packet

    def _save(self, packet):
        write_json(self._path, packet)

    def _sort(self, items):
        return sorted(
            items,
            key=lambda item: (
                float(item.created or 0.0),
                str(item.name or "").lower(),
            ),
        )

    def _name(self, value):
        return str(value or "").strip()

    def _kind(self, value):
        return str(value or "").strip().lower()

    def _link(self, value):
        return str(value or "").strip()
