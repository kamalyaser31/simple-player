class PlayerStateMixin:
    def is_shuffle_enabled(self):
        return self._state.is_shuffle_enabled()

    def set_shuffle_enabled(self, enabled):
        return self._state.set_shuffle_enabled(enabled)

    def toggle_shuffle(self):
        return self._state.toggle_shuffle()

    def is_repeat_file_enabled(self):
        return self._state.is_repeat_file_enabled()

    def set_repeat_file_enabled(self, enabled):
        return self._state.set_repeat_file_enabled(enabled)

    def toggle_repeat_file(self):
        return self._state.toggle_repeat_file()

    def is_wrap_playlist_enabled(self):
        return bool(self._wrap_playlist_enabled)

    def set_wrap_playlist_enabled(self, enabled):
        self._wrap_playlist_enabled = bool(enabled)
        return self._wrap_playlist_enabled

    def toggle_mark_current(self):
        return self._state.toggle_mark_current()

    def toggle_mark_all(self):
        return self._state.toggle_mark_all()

    def clear_marked_files(self):
        return self._state.clear_marked()

    def is_current_marked(self):
        return self._state.is_current_marked()

    def are_all_files_marked(self):
        return self._state.are_all_marked()

    def has_marked_files(self):
        return self._state.has_marked_files()

    def get_marked_files_count(self):
        return self._state.get_marked_count()

    def get_marked_files(self):
        return self._state.get_marked_files()

    def get_file_list(self):
        return self._state.get_file_list()

    def get_title(self, path):
        return self._state.get_title(path)

    def get_count(self):
        return self._state.get_count()

    def get_current_index(self):
        return self._state.get_current_index()

    def set_pending_start(self, value):
        self._state.set_pending_start(value)

    def jump_to_index(self, index):
        if not self._state.jump_to_index(index):
            return False
        return self._load_current()
