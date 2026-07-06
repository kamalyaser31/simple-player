import os


class PlaylistStateMetaMixin:
    def get_title(self, path):
        meta = self._get_meta(path)
        if not meta:
            return ""
        return str(meta.get("title") or "")

    def get_source(self, path):
        meta = self._get_meta(path)
        if not meta:
            return ""
        return str(meta.get("source") or "")

    def has_source(self, source):
        target = str(source or "").strip()
        if not target:
            return False
        for path in self._file_list:
            if str(self.get_source(path) or "").strip() == target:
                return True
        return False

    def _set_meta(self, path, title=None, source=None):
        key = self._path_key(path)
        data = {}
        if title:
            data["title"] = str(title)
        if source:
            data["source"] = str(source)
        if data:
            self._meta[key] = data
        elif key in self._meta:
            self._meta.pop(key, None)

    def _get_meta(self, path):
        if not path:
            return None
        return self._meta.get(self._path_key(path))

    def _path_key(self, path):
        text = str(path or "")
        if "://" in text:
            return text
        return os.path.normcase(os.path.abspath(text))
