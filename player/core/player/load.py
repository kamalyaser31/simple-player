class PlayerLoadMixin:
    def open_file(self, path, start_position=None):
        if not self._state.open_file(path, start_position=start_position):
            return False
        return self._load_current()

    def open_folder(self, folder_path):
        if not self._state.open_folder(
            folder_path, recursive=False, preserve_current=True
        ):
            return False
        return self._load_current()

    def open_file_with_folder(self, path, recursive=False, start_position=None):
        if not self._state.open_file_with_folder(
            path, recursive=recursive, start_position=start_position
        ):
            return False
        return self._load_current()

    def open_file_list(self, files, preferred_path=None, start_position=None):
        if not self._state.open_file_list(
            files,
            preferred_path=preferred_path,
            start_position=start_position,
        ):
            return False
        return self._load_current()

    def open_stream(self, url, append=True, start_position=None, title=None, source_url=None):
        if append:
            if not self._state.append(
                url,
                jump=True,
                start_position=start_position,
                title=title,
                source=source_url,
            ):
                return False
        else:
            if not self._state.open_file(
                url,
                start_position=start_position,
                title=title,
                source=source_url,
            ):
                return False
        return self._load_current()

    def queue_stream(self, url, title=None, source_url=None):
        return self._state.append(url, jump=False, title=title, source=source_url)

    def next_track(self):
        if not self._state.next_track(
            use_shuffle=True,
            wrap=self._wrap_playlist_enabled,
        ):
            return False
        return self._load_current()

    def previous_track(self):
        if not self._state.previous_track(
            use_shuffle=True,
            wrap=self._wrap_playlist_enabled,
        ):
            return False
        return self._load_current()

    def go_to_first_file(self):
        if not self._state.go_to_first():
            return False
        return self._load_current()

    def go_to_last_file(self):
        if not self._state.go_to_last():
            return False
        return self._load_current()

    def reload_current_file(self):
        return self._load_current()

    def _load_current(self):
        path = self._state.current_path
        if not path:
            return False
        start = self._state.pop_pending_start()
        # Loop points must not leak between tracks/streams.
        self._engine.clear_loop()
        loaded = self._engine.load_file(path, start_position=start, paused=False)
        if loaded:
            self._apply_active_audio_filters()
        return loaded
