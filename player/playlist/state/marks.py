class PlaylistStateMarksMixin:
    def toggle_mark_current(self):
        path = self._current_path
        if not path:
            return None, None
        key = self._path_key(path)
        if key in self._marked_keys:
            self._marked_keys.discard(key)
            return False, path
        self._marked_keys.add(key)
        return True, path

    def toggle_mark_all(self):
        if not self._file_list:
            return False
        if self.are_all_marked():
            self._clear_marked()
            return False
        self._marked_keys = {self._path_key(path) for path in self._file_list}
        return True

    def clear_marked(self):
        had_any = bool(self._marked_keys)
        self._clear_marked()
        return had_any

    def is_current_marked(self):
        if not self._current_path:
            return False
        return self._path_key(self._current_path) in self._marked_keys

    def are_all_marked(self):
        if not self._file_list:
            return False
        return all(self._path_key(path) in self._marked_keys for path in self._file_list)

    def has_marked_files(self):
        return bool(self.get_marked_files())

    def get_marked_count(self):
        return len(self.get_marked_files())

    def get_marked_files(self):
        if not self._marked_keys:
            return []
        return [path for path in self._file_list if self._path_key(path) in self._marked_keys]

    def _clear_marked(self):
        self._marked_keys.clear()
