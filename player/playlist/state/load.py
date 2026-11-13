import os

from core.media_library import collect_audio_files


def _sibling_index(entries, path):
    """Index that keeps path in name order among files of its own folder."""
    folder = os.path.normcase(os.path.dirname(os.path.abspath(path)))
    name = os.path.basename(path).lower()
    last_sibling = None
    for idx, entry in enumerate(entries):
        if os.path.normcase(os.path.dirname(os.path.abspath(entry))) != folder:
            continue
        if os.path.basename(entry).lower() > name:
            return idx
        last_sibling = idx
    return len(entries) if last_sibling is None else last_sibling + 1


class PlaylistStateLoadMixin:
    def open_file_list(self, files, preferred_path=None, start_position=None):
        entries = list(files or [])
        if not entries:
            return False

        selected = None
        if preferred_path:
            target = os.path.normcase(os.path.abspath(preferred_path))
            for entry in entries:
                if os.path.normcase(os.path.abspath(entry)) == target:
                    selected = entry
                    break
            # A video opened from Explorer is not collected by the audio-only
            # folder scan; keep it in the list so playback starts with it.
            if selected is None and os.path.isfile(preferred_path):
                entries.insert(_sibling_index(entries, preferred_path), preferred_path)
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

    def open_folder(
        self, folder_path, recursive=False, preferred_path=None, preserve_current=False
    ):
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
        return self.open_file_list(
            files, preferred_path=path, start_position=start_position
        )
