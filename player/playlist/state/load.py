import os

from core.media_library import collect_audio_files


class PlaylistStateLoadMixin:
    def open_file_list(self, files, preferred_path=None, start_position=None):
        entries = list(files or [])
        if not entries:
            return False

        selected = None
        if preferred_path and preferred_path in entries:
            selected = preferred_path

        if selected is None:
            index = 0
            pending = None
        else:
            index = entries.index(selected)
            pending = start_position

        self._file_list = entries
        self._current_index = index
        self._current_path = self._file_list[index]
        self._pending_start = pending
        self._meta = {}
        self._clear_marked()
        self._rebuild_shuffle_order()
        return True

    def open_file(self, path, start_position=None, title=None, source=None):
        if not path:
            return False
        self._file_list = [path]
        self._current_index = 0
        self._current_path = path
        self._pending_start = start_position
        self._meta = {}
        self._set_meta(path, title=title, source=source)
        self._clear_marked()
        self._rebuild_shuffle_order()
        return True

    def append_and_jump(self, path, start_position=None, title=None, source=None):
        return self.append(
            path,
            jump=True,
            start_position=start_position,
            title=title,
            source=source,
        )

    def append(self, path, jump=False, start_position=None, title=None, source=None):
        if not path:
            return False
        if not self._file_list:
            return self.open_file(
                path,
                start_position=start_position,
                title=title,
                source=source,
            )
        self._file_list.append(path)
        self._set_meta(path, title=title, source=source)
        if jump:
            self._current_index = len(self._file_list) - 1
            self._current_path = path
            self._pending_start = start_position
        if self._shuffle_enabled:
            self._rebuild_shuffle_order()
        else:
            self._clear_shuffle_order()
        return True

    def open_folder(self, folder_path, recursive=False, preferred_path=None, preserve_current=False):
        files = collect_audio_files(folder_path, recursive=recursive)
        if not files:
            return False
        selected = None
        if preferred_path and preferred_path in files:
            selected = preferred_path
        elif preserve_current and self._current_path and self._current_path in files:
            selected = self._current_path
        return self.open_file_list(files, preferred_path=selected, start_position=None)

    def open_file_with_folder(self, path, recursive=False, start_position=None):
        if not path:
            return False
        folder_path = os.path.dirname(path)
        files = collect_audio_files(folder_path, recursive=recursive)
        if not files:
            return False
        return self.open_file_list(files, preferred_path=path, start_position=start_position)
