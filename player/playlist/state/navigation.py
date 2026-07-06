class PlaylistStateNavigationMixin:
    def next_track(self, use_shuffle=True, wrap=False):
        if use_shuffle and self._shuffle_enabled:
            return self._next_with_shuffle(wrap=wrap)
        return self._next_sequential(wrap=wrap)

    def previous_track(self, use_shuffle=True, wrap=False):
        if use_shuffle and self._shuffle_enabled:
            return self._previous_with_shuffle(wrap=wrap)
        return self._previous_sequential(wrap=wrap)

    def jump_to_index(self, index):
        if index < 0 or index >= len(self._file_list):
            return False
        self._current_index = index
        self._current_path = self._file_list[index]
        self._pending_start = None
        self._sync_shuffle_position_to_current()
        return True

    def go_to_first(self):
        if not self._file_list or self._current_index <= 0:
            return False
        self._current_index = 0
        self._current_path = self._file_list[0]
        self._pending_start = None
        self._sync_shuffle_position_to_current()
        return True

    def go_to_last(self):
        if not self._file_list:
            return False
        target = len(self._file_list) - 1
        if self._current_index == target:
            return False
        self._current_index = target
        self._current_path = self._file_list[target]
        self._pending_start = None
        self._sync_shuffle_position_to_current()
        return True

    def clear_current(self):
        self._current_path = None
        self._current_index = -1
        self._pending_start = None
        self._clear_shuffle_order()

    def clear_all(self):
        self._file_list = []
        self._current_path = None
        self._current_index = -1
        self._pending_start = None
        self._meta = {}
        self._clear_marked()
        self._clear_shuffle_order()

    def is_shuffle_enabled(self):
        return self._shuffle_enabled

    def set_shuffle_enabled(self, enabled):
        self._shuffle_enabled = bool(enabled)
        if self._shuffle_enabled:
            self._rebuild_shuffle_order()
        else:
            self._clear_shuffle_order()
        return self._shuffle_enabled

    def toggle_shuffle(self):
        return self.set_shuffle_enabled(not self._shuffle_enabled)

    def is_repeat_file_enabled(self):
        return self._repeat_file_enabled

    def set_repeat_file_enabled(self, enabled):
        self._repeat_file_enabled = bool(enabled)
        return self._repeat_file_enabled

    def toggle_repeat_file(self):
        return self.set_repeat_file_enabled(not self._repeat_file_enabled)

    def _next_sequential(self, wrap=False):
        if len(self._file_list) <= 1:
            return False
        if self._current_index + 1 >= len(self._file_list):
            if not wrap:
                return False
            self._current_index = 0
        else:
            self._current_index += 1
        self._current_path = self._file_list[self._current_index]
        self._pending_start = None
        self._sync_shuffle_position_to_current()
        return True

    def _previous_sequential(self, wrap=False):
        if len(self._file_list) <= 1:
            return False
        if self._current_index - 1 < 0:
            if not wrap:
                return False
            self._current_index = len(self._file_list) - 1
        else:
            self._current_index -= 1
        self._current_path = self._file_list[self._current_index]
        self._pending_start = None
        self._sync_shuffle_position_to_current()
        return True

    def _next_with_shuffle(self, wrap=False):
        if len(self._file_list) <= 1:
            return False
        self._sync_shuffle_position_to_current()
        if self._shuffle_position + 1 >= len(self._shuffle_order):
            if not wrap:
                return False
            self._shuffle_position = 0
        else:
            self._shuffle_position += 1
        self._current_index = self._shuffle_order[self._shuffle_position]
        self._current_path = self._file_list[self._current_index]
        self._pending_start = None
        return True

    def _previous_with_shuffle(self, wrap=False):
        if len(self._file_list) <= 1:
            return False
        self._sync_shuffle_position_to_current()
        if self._shuffle_position <= 0:
            if not wrap:
                return False
            self._shuffle_position = len(self._shuffle_order) - 1
        else:
            self._shuffle_position -= 1
        self._current_index = self._shuffle_order[self._shuffle_position]
        self._current_path = self._file_list[self._current_index]
        self._pending_start = None
        return True

    def _sync_shuffle_position_to_current(self):
        if not self._shuffle_enabled:
            return
        if self._current_index < 0 or self._current_index >= len(self._file_list):
            self._clear_shuffle_order()
            return
        if not self._is_shuffle_order_valid():
            self._rebuild_shuffle_order()
            return
        try:
            self._shuffle_position = self._shuffle_order.index(self._current_index)
        except ValueError:
            self._rebuild_shuffle_order()

    def _rebuild_shuffle_order(self):
        if not self._shuffle_enabled:
            return
        if self._current_index < 0 or self._current_index >= len(self._file_list):
            self._clear_shuffle_order()
            return
        count = len(self._file_list)
        if count == 0:
            self._clear_shuffle_order()
            return

        current = self._current_index
        order = [idx for idx in range(count) if idx != current]
        self._rng.shuffle(order)
        insert_pos = min(max(current, 0), len(order))
        order.insert(insert_pos, current)
        self._shuffle_order = order
        self._shuffle_position = insert_pos

    def _is_shuffle_order_valid(self):
        count = len(self._file_list)
        if count == 0:
            return False
        if len(self._shuffle_order) != count:
            return False
        return set(self._shuffle_order) == set(range(count))

    def _clear_shuffle_order(self):
        self._shuffle_order = []
        self._shuffle_position = -1
