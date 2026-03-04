import wx
from gettext import gettext as _

from actions import (
    ADD_BOOKMARK,
    CHECK_APP_UPDATES,
    CLOSE_FILE,
    CLOSE_ALL_FILES,
    GO_TO_FILE,
    GO_TO_TIME,
    OPEN_ABOUT,
    OPEN_CHANGES,
    OPEN_CONTAINING_FOLDER,
    OPEN_FILE,
    OPEN_FILE_LIST,
    OPEN_FILE_PROPERTIES,
    OPEN_LINK,
    OPEN_CONTACT_EMAIL,
    OPEN_CONTACT_TELEGRAM,
    OPEN_CONTACT_WEBSITE,
    OPEN_FOLDER,
    OPEN_SETTINGS,
    OPEN_USER_GUIDE,
    OPEN_YOUTUBE_LINK,
    OPEN_YOUTUBE_SEARCH,
    MANAGE_BOOKMARKS,
    REC_PAUSE,
    REC_START,
    REC_STOP,
    UPDATE_YT_COMPONENTS,
    VIDEO_DESCRIPTION,
    VIDEO_DOWNLOAD,
)
from ui.accelerators import build_accelerator_table


class MainFrameStateMixin:
    def _build_shortcuts(self):
        reserved_ids = {
            OPEN_FILE: self._open_file_item.GetId(),
            OPEN_LINK: self._open_link_item.GetId(),
            OPEN_YOUTUBE_LINK: self._open_yt_link_item.GetId(),
            OPEN_YOUTUBE_SEARCH: self._open_yt_search_item.GetId(),
            VIDEO_DOWNLOAD: self._video_dl_item.GetId(),
            VIDEO_DESCRIPTION: self._video_desc_item.GetId(),
            OPEN_FOLDER: self._open_folder_item.GetId(),
            OPEN_CONTAINING_FOLDER: self._open_containing_item.GetId(),
            OPEN_FILE_PROPERTIES: self._open_file_props_item.GetId(),
            OPEN_FILE_LIST: self._open_file_list_item.GetId(),
            CLOSE_FILE: self._close_file_item.GetId(),
            CLOSE_ALL_FILES: self._close_all_files_item.GetId(),
            OPEN_SETTINGS: self._settings_item.GetId(),
            OPEN_USER_GUIDE: self._user_guide_item.GetId(),
            OPEN_CHANGES: self._changes_item.GetId(),
            OPEN_CONTACT_EMAIL: self._contact_email_item.GetId(),
            OPEN_CONTACT_TELEGRAM: self._contact_tg_item.GetId(),
            OPEN_CONTACT_WEBSITE: self._contact_web_item.GetId(),
            CHECK_APP_UPDATES: self._check_updates_item.GetId(),
            UPDATE_YT_COMPONENTS: self._update_yt_item.GetId(),
            OPEN_ABOUT: self._about_item.GetId(),
            ADD_BOOKMARK: self._bookmark_add_item.GetId(),
            MANAGE_BOOKMARKS: self._bookmark_manage_item.GetId(),
            GO_TO_FILE: self._go_to_file_item.GetId(),
            GO_TO_TIME: self._go_to_time_item.GetId(),
            REC_START: self._rec_start_item.GetId(),
            REC_PAUSE: self._rec_pause_item.GetId(),
            REC_STOP: self._rec_stop_item.GetId(),
        }
        table, action_map = build_accelerator_table(
            self._controller.get_shortcut_bindings(),
            reserved_ids,
        )
        self._action_id_map = action_map
        self.SetAcceleratorTable(table)
        if self._action_id_map and not self._accelerator_bound:
            self.Bind(wx.EVT_MENU, self._on_accelerator)
            self._accelerator_bound = True

    def refresh_shortcuts(self):
        self._build_shortcuts()

    def set_playing(self, is_playing):
        self._play_button.SetLabel(_("Pause") if is_playing else _("Play"))

    def set_shuffle_checked(self, enabled):
        self._shuffle_item.Check(bool(enabled))

    def set_repeat_file_checked(self, enabled):
        self._repeat_file_item.Check(bool(enabled))

    def set_silence_removal_checked(self, enabled):
        self._silence_removal_item.Check(bool(enabled))

    def set_mark_current_checked(self, enabled):
        self._mark_current_item.Check(bool(enabled))

    def set_mark_all_checked(self, enabled):
        self._mark_all_item.Check(bool(enabled))

    def set_marked_actions_enabled(self, enabled):
        self._has_marked_files = bool(enabled)
        can_use = self._has_marked_files and self._file_loaded
        for item in self._marked_actions_items:
            item.Enable(can_use)
        if self._marked_actions_menu_index >= 0 and self.GetMenuBar() is not None:
            try:
                self.GetMenuBar().EnableTop(self._marked_actions_menu_index, can_use)
            except Exception:
                pass

    def set_video_options_enabled(self, enabled):
        self._video_opts_enabled = bool(enabled) and self._file_loaded
        for item in self._video_opts_items:
            item.Enable(self._video_opts_enabled)
        if self._video_opts_menu_index >= 0 and self.GetMenuBar() is not None:
            try:
                self.GetMenuBar().EnableTop(
                    self._video_opts_menu_index,
                    self._video_opts_enabled,
                )
            except Exception:
                pass

    def set_file_properties_enabled(self, enabled):
        self._file_props_enabled = bool(enabled) and self._file_loaded
        self._open_file_props_item.Enable(self._file_props_enabled)

    def set_local_file_actions_enabled(self, enabled):
        self._local_file_actions_enabled = bool(enabled) and self._file_loaded
        self._rename_item.Enable(self._local_file_actions_enabled)
        self._delete_item.Enable(self._local_file_actions_enabled)

    def set_bookmarks_enabled(self, enabled):
        self._bookmarks_enabled = bool(enabled) and self._file_loaded
        self._bookmark_add_item.Enable(self._bookmarks_enabled)
        self._bookmark_manage_item.Enable(self._bookmarks_enabled)
        menu_bar = self.GetMenuBar()
        if menu_bar is not None:
            for item_id in self._bookmark_jump_ids:
                menu_item = menu_bar.FindItemById(item_id)
                if menu_item:
                    menu_item.Enable(self._bookmarks_enabled)
            if self._bookmarks_menu_index >= 0:
                try:
                    menu_bar.EnableTop(self._bookmarks_menu_index, self._bookmarks_enabled)
                except Exception:
                    pass

    def set_file_loaded(self, loaded):
        self._file_loaded = bool(loaded)
        enabled = self._file_loaded
        for item in (
            self._open_containing_item,
            self._open_file_props_item,
            self._open_file_list_item,
            self._close_file_item,
            self._close_all_files_item,
            self._copy_current_item,
            self._mark_current_item,
            self._mark_all_item,
            self._clear_marked_item,
            self._play_pause_item,
            self._speed_up_item,
            self._speed_down_item,
            self._reset_speed_item,
            self._prev_item,
            self._next_item,
            self._first_item,
            self._go_to_file_item,
            self._last_item,
            self._shuffle_item,
            self._repeat_file_item,
            self._silence_removal_item,
            self._loop_start_item,
            self._loop_end_item,
            self._loop_clear_item,
            self._rewind_item,
            self._forward_item,
            self._start_item,
            self._end_item,
            self._go_to_time_item,
        ):
            item.Enable(enabled)
        if not enabled:
            self._mark_current_item.Check(False)
            self._mark_all_item.Check(False)

        menu_bar = self.GetMenuBar()
        if menu_bar is not None:
            for item_id in self._jump_menu_map:
                menu_item = menu_bar.FindItemById(item_id)
                if menu_item:
                    menu_item.Enable(enabled)
            for item_id in self._seek_step_menu_map:
                menu_item = menu_bar.FindItemById(item_id)
                if menu_item:
                    menu_item.Enable(enabled)

        self.set_marked_actions_enabled(self._has_marked_files if enabled else False)
        self.set_file_properties_enabled(self._file_props_enabled if enabled else False)
        self.set_local_file_actions_enabled(
            self._local_file_actions_enabled if enabled else False
        )
        self.set_video_options_enabled(self._video_opts_enabled if enabled else False)
        self.set_bookmarks_enabled(self._bookmarks_enabled if enabled else False)

    def set_recording_state(self, running, paused):
        is_running = bool(running)
        is_paused = bool(paused) and is_running

        self._recording_running = is_running
        self._recording_paused = is_paused

        self._rec_start_item.Enable(not is_running)
        self._rec_pause_item.Enable(is_running)
        self._rec_stop_item.Enable(is_running)

        pause_label = _("Resume") if is_paused else _("Pause")
        self._rec_pause_item.SetItemLabel(
            self._menu_label(pause_label, REC_PAUSE)
        )
