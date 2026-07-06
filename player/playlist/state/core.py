class PlaylistStateCoreMixin:
    @property
    def current_path(self):
        return self._current_path

    @property
    def pending_start(self):
        return self._pending_start

    @property
    def current_title(self):
        return self.get_title(self._current_path)

    @property
    def current_source(self):
        return self.get_source(self._current_path)

    def pop_pending_start(self):
        value = self._pending_start
        self._pending_start = None
        return value

    def set_pending_start(self, value):
        self._pending_start = value

    def get_file_list(self):
        return list(self._file_list)

    def get_count(self):
        return len(self._file_list)

    def get_current_index(self):
        return self._current_index
