END_FILE_REASON_EOF = 0
END_FILE_REASON_ERROR = 4


class PlayerLifecycleMixin:
    def _on_end_file_event(self, event):
        info = event.get("event") or {}
        reason = info.get("reason")
        if reason not in (END_FILE_REASON_EOF, END_FILE_REASON_ERROR):
            return
        self._handle_finished_file()

    def _handle_finished_file(self):
        if not self._state.current_path:
            return
        if self._state.is_repeat_file_enabled():
            self._state.set_pending_start(0)
            self._load_current()
            return
        if self._end_behavior == "advance":
            if not self._state.next_track(
                use_shuffle=True,
                wrap=self._wrap_playlist_enabled,
            ):
                self.stop()
            else:
                self._load_current()
            return
        if self._end_behavior == "loop":
            self._state.set_pending_start(0)
            self._load_current()
