import os
import time

from .fileio import read_json, write_json
from .model import Pos, pos_from_dict, pos_to_dict


class PosStore:
    def __init__(self, settings_path, filename="positions.json"):
        settings_file = str(settings_path or "").strip()
        root = os.path.dirname(settings_file) if settings_file else ""
        self._path = os.path.join(root, filename) if root else filename

    @property
    def path(self):
        return self._path

    def get(self, media_path):
        path = str(media_path or "").strip()
        key = self._key(path)
        if not key:
            return None
        packet = self._load()
        files = packet.get("files")
        if not isinstance(files, dict):
            return None
        raw = files.get(key)
        item = pos_from_dict(raw, fallback_path=path)
        if item is None:
            return None
        return float(item.pos or 0.0)

    def set(self, media_path, pos):
        path = str(media_path or "").strip()
        key = self._key(path)
        if not key:
            return False
        value = self._pos(pos)
        packet = self._load()
        files = packet.get("files")
        if not isinstance(files, dict):
            files = {}
            packet["files"] = files
        item = Pos(path=path, pos=value, updated=time.time())
        files[key] = pos_to_dict(item)
        self._save(packet)
        return True

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

    def _key(self, media_path):
        raw = str(media_path or "").strip()
        if not raw:
            return ""
        low = raw.lower()
        if low.startswith("http://") or low.startswith("https://"):
            return raw
        return os.path.normcase(os.path.abspath(raw))

    def _pos(self, value):
        try:
            pos = float(value)
        except (TypeError, ValueError):
            pos = 0.0
        if pos < 0:
            pos = 0.0
        return pos
