import os
import time
import uuid

from .fileio import read_json, write_json
from .model import Mark, mark_from_dict, mark_to_dict


class MarkStore:
    def __init__(self, settings_path, filename="bookmarks.json"):
        settings_file = str(settings_path or "").strip()
        root = os.path.dirname(settings_file) if settings_file else ""
        self._path = os.path.join(root, filename) if root else filename

    @property
    def path(self):
        return self._path

    def list_for(self, media_path):
        key = self._key(media_path)
        if not key:
            return []
        packet = self._load()
        rows = self._rows(packet, key)
        marks = []
        for row in rows:
            mark = mark_from_dict(row, fallback_path=media_path)
            if mark is None:
                continue
            marks.append(mark)
        return self._sort(marks)

    def add(self, media_path, pos, name):
        path = str(media_path or "").strip()
        key = self._key(path)
        if not key:
            raise ValueError("Invalid media path.")
        text = self._name(name)
        if not text:
            raise ValueError("Bookmark name is required.")
        mark = Mark(
            id=uuid.uuid4().hex,
            name=text,
            path=path,
            pos=self._pos(pos),
            created=time.time(),
        )
        packet = self._load()
        rows = self._rows(packet, key)
        rows.append(mark_to_dict(mark))
        self._set_rows(packet, key, rows)
        self._save(packet)
        return mark

    def rename(self, media_path, mark_id, name):
        key = self._key(media_path)
        target_id = str(mark_id or "").strip()
        text = self._name(name)
        if not key or not target_id or not text:
            return False
        packet = self._load()
        rows = self._rows(packet, key)
        changed = False
        for row in rows:
            if str(row.get("id") or "").strip() != target_id:
                continue
            row["name"] = text
            changed = True
            break
        if not changed:
            return False
        self._set_rows(packet, key, rows)
        self._save(packet)
        return True

    def delete(self, media_path, mark_id):
        key = self._key(media_path)
        target_id = str(mark_id or "").strip()
        if not key or not target_id:
            return False
        packet = self._load()
        rows = self._rows(packet, key)
        kept = [row for row in rows if str(row.get("id") or "").strip() != target_id]
        if len(kept) == len(rows):
            return False
        self._set_rows(packet, key, kept)
        self._save(packet)
        return True

    def slot(self, media_path, slot):
        try:
            idx = int(slot) - 1
        except (TypeError, ValueError):
            return None
        if idx < 0:
            return None
        marks = self.list_for(media_path)
        if idx >= len(marks):
            return None
        return marks[idx]

    def _load(self):
        packet = read_json(self._path)
        if not isinstance(packet, dict):
            packet = {}
        if not isinstance(packet.get("files"), dict):
            packet["files"] = {}
        if "version" not in packet:
            packet["version"] = 1
        return packet

    def _save(self, packet):
        write_json(self._path, packet)

    def _rows(self, packet, key):
        files = packet.get("files")
        if not isinstance(files, dict):
            files = {}
            packet["files"] = files
        rows = files.get(key)
        if not isinstance(rows, list):
            rows = []
        return list(rows)

    def _set_rows(self, packet, key, rows):
        files = packet.get("files")
        if not isinstance(files, dict):
            files = {}
            packet["files"] = files
        if rows:
            files[key] = rows
        else:
            files.pop(key, None)

    def _key(self, media_path):
        raw = str(media_path or "").strip()
        if not raw:
            return ""
        low = raw.lower()
        if low.startswith("http://") or low.startswith("https://"):
            return raw
        return os.path.normcase(os.path.abspath(raw))

    def _name(self, name):
        return str(name or "").strip()

    def _pos(self, value):
        try:
            pos = float(value)
        except (TypeError, ValueError):
            pos = 0.0
        if pos < 0:
            pos = 0.0
        return pos

    def _sort(self, marks):
        return sorted(
            marks,
            key=lambda item: (
                float(item.pos or 0.0),
                float(item.created or 0.0),
                str(item.name or "").lower(),
            ),
        )
