class PlayerWindowMixin:
    @property
    def current_path(self):
        return self._state.current_path

    @property
    def current_title(self):
        return self._state.current_title

    @property
    def current_source(self):
        return self._state.current_source

    def shutdown(self):
        self._engine.terminate()

    def set_render_window(self, window_handle):
        window_id = self._normalize_window_handle(window_handle)
        if window_id is None:
            return False
        if self._engine.try_set_window_id(window_id):
            self._render_window_id = window_id
            return True
        return self._recreate_with_window(window_id)

    def _normalize_window_handle(self, window_handle):
        if not window_handle:
            return None
        try:
            window_id = int(window_handle)
        except (TypeError, ValueError):
            return None
        if window_id < 0:
            window_id &= 0xFFFFFFFF
        if window_id <= 0:
            return None
        return window_id

    def _recreate_with_window(self, window_id):
        snapshot = self._engine.recreate_with_window(window_id)
        if snapshot is None:
            return False

        self._engine.set_end_behavior(self._end_behavior)
        self._engine.restore_runtime_state(snapshot)
        self._render_window_id = window_id

        if self._state.current_path:
            self._state.set_pending_start(snapshot.get("resume_at"))
            self._load_current()
            if snapshot.get("paused"):
                self.pause()
        return True
