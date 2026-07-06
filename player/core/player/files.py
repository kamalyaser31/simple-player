import os


class PlayerFilesMixin:
    def stop(self):
        self._stop_core_only()
        self._state.clear_current()

    def delete_current_file(self):
        path = self.current_path
        if not path or not os.path.isfile(path):
            return False, None
        resume_at = self.get_elapsed()
        self._stop_core_only()
        try:
            os.remove(path)
        except OSError:
            self._state.set_pending_start(resume_at)
            self._load_current()
            return False, None

        changed, current_changed = self._state.remove_paths([path])
        if not changed:
            return False, None
        if self._state.current_path is None:
            return True, None
        if current_changed:
            self._load_current()
        return True, self._state.current_path

    def close_current_file(self):
        path = self.current_path
        if not path:
            return False, None
        self._stop_core_only()
        changed, current_changed = self._state.remove_paths([path])
        if not changed:
            return False, None
        if self._state.current_path is None:
            return True, None
        if current_changed:
            self._load_current()
        return True, self._state.current_path

    def close_all_files(self):
        if not self.current_path and not self._state.get_count():
            return False
        self._stop_core_only()
        self._state.clear_all()
        return True

    def rename_current_file(self, new_name):
        path = self.current_path
        if not path or not new_name:
            return False, None
        directory = os.path.dirname(path)
        _, ext = os.path.splitext(path)
        base, new_ext = os.path.splitext(new_name)
        if not base:
            return False, None
        if not new_ext:
            new_name = f"{new_name}{ext}"
        new_path = os.path.join(directory, new_name)
        if os.path.exists(new_path):
            return False, None

        resume_at = self.get_elapsed()
        self._stop_core_only()
        try:
            os.rename(path, new_path)
        except OSError:
            self._state.set_pending_start(resume_at)
            self._load_current()
            return False, None

        self._state.replace_path(path, new_path)
        self._state.set_pending_start(resume_at)
        self._load_current()
        return True, new_path

    def remove_files(self, paths):
        if not paths:
            return False
        current = self.current_path
        remove_keys = {
            os.path.normcase(os.path.abspath(path))
            for path in paths
            if path
        }
        if current and os.path.normcase(os.path.abspath(current)) in remove_keys:
            self._stop_core_only()

        changed, current_changed = self._state.remove_paths(paths)
        if not changed:
            return False
        if self._state.current_path and current_changed:
            self._load_current()
        return True

    def remove_sources(self, sources):
        changed, _current_changed = self._state.remove_sources(sources)
        return bool(changed)

    def _stop_core_only(self):
        self._engine.stop()
