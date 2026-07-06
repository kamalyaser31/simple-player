class PlaylistStateMutationsMixin:
    def remove_paths(self, paths):
        if not paths:
            return False, False

        old_current = self._current_path
        old_index = self._current_index
        remove_keys = {self._path_key(path) for path in paths if path}
        if not remove_keys:
            return False, False

        new_list = [p for p in self._file_list if self._path_key(p) not in remove_keys]
        changed = len(new_list) != len(self._file_list)
        if not changed:
            return False, False

        self._file_list = new_list
        self._marked_keys = {k for k in self._marked_keys if k not in remove_keys}
        self._meta = {
            key: value
            for key, value in self._meta.items()
            if key not in remove_keys
        }

        current_changed = False
        if not self._file_list:
            self._current_index = -1
            self._current_path = None
            self._pending_start = None
            self._clear_shuffle_order()
            return True, old_current is not None

        if old_current is None:
            self._current_index = -1
            self._current_path = None
            self._pending_start = None
            self._clear_shuffle_order()
            return True, False

        if old_current and old_current in self._file_list:
            self._current_index = self._file_list.index(old_current)
            self._current_path = old_current
        else:
            self._current_index = min(max(old_index, 0), len(self._file_list) - 1)
            self._current_path = self._file_list[self._current_index]
            self._pending_start = None
            current_changed = True

        if self._shuffle_enabled:
            self._rebuild_shuffle_order()
        else:
            self._clear_shuffle_order()
        return True, current_changed

    def remove_sources(self, sources):
        source_set = {
            str(value or "").strip()
            for value in (sources or [])
            if str(value or "").strip()
        }
        if not source_set:
            return False, False
        paths = []
        for path in self._file_list:
            source = str(self.get_source(path) or "").strip()
            if source and source in source_set:
                paths.append(path)
        if not paths:
            return False, False
        return self.remove_paths(paths)

    def replace_path(self, old_path, new_path):
        if not old_path or not new_path:
            return False
        try:
            index = self._file_list.index(old_path)
        except ValueError:
            return False

        self._file_list[index] = new_path
        if self._current_path == old_path:
            self._current_path = new_path

        old_key = self._path_key(old_path)
        new_key = self._path_key(new_path)
        if old_key in self._meta:
            self._meta[new_key] = self._meta.pop(old_key)
        if old_key in self._marked_keys:
            self._marked_keys.discard(old_key)
            self._marked_keys.add(new_key)

        self._sync_shuffle_position_to_current()
        return True
