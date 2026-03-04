import wx
from gettext import gettext as _

from actions import (
    ADD_BOOKMARK,
    BOOKMARK_JUMPS,
    CHECK_APP_UPDATES,
    CLEAR_SELECTION,
    CLEAR_MARKED_FILES,
    CLOSE_FILE,
    CLOSE_ALL_FILES,
    COPY_CURRENT_FILE,
    DELETE_FILE,
    END_SELECTION,
    GO_TO_FILE,
    GO_TO_TIME,
    GO_FIRST_FILE,
    GO_LAST_FILE,
    MARKED_COPY_TO_CLIPBOARD,
    MARKED_COPY_TO_FOLDER,
    MARKED_DELETE,
    MARKED_MOVE_TO_FOLDER,
    MARK_ALL_FILES,
    MARK_CURRENT_FILE,
    MANAGE_BOOKMARKS,
    NEXT_TRACK,
    OPEN_CONTAINING_FOLDER,
    OPEN_FILE,
    OPEN_FILE_LIST,
    OPEN_FILE_PROPERTIES,
    OPEN_FOLDER,
    OPEN_LINK,
    OPEN_SETTINGS,
    OPEN_YOUTUBE_LINK,
    OPEN_YOUTUBE_SEARCH,
    PASTE_FROM_CLIPBOARD,
    PLAY_PAUSE,
    PREVIOUS_TRACK,
    REC_PAUSE,
    REC_START,
    REC_STOP,
    RENAME_FILE,
    RESET_SPEED,
    SEEK_BACKWARD,
    SEEK_END,
    SEEK_FORWARD,
    SEEK_START,
    SEEK_STEP_0,
    SEEK_STEP_1,
    SEEK_STEP_2,
    SEEK_STEP_3,
    SEEK_STEP_4,
    SEEK_STEP_5,
    SEEK_STEP_6,
    SEEK_STEP_7,
    SEEK_STEP_8,
    SEEK_STEP_9,
    SEEK_STEP_CUSTOM,
    SOUND_CARDS,
    SPEED_DOWN,
    SPEED_UP,
    START_SELECTION,
    TEST_SPEAKERS,
    TOGGLE_REPEAT_FILE,
    TOGGLE_SHUFFLE,
    TOGGLE_SILENCE_REMOVAL,
    OPEN_USER_GUIDE,
    OPEN_CHANGES,
    OPEN_CONTACT_EMAIL,
    OPEN_CONTACT_TELEGRAM,
    OPEN_CONTACT_WEBSITE,
    OPEN_ABOUT,
    VIDEO_COPY_LINK,
    VIDEO_DESCRIPTION,
    VIDEO_DOWNLOAD,
    UPDATE_YT_COMPONENTS,
    PERCENT_JUMPS,
)
from app_actions.playback_actions import SEEK_STEP_LABELS
from config.shortcut_utils import shortcut_to_display


class MainFrameMenuMixin:
    def _build_menu(self):
        menu_bar = wx.MenuBar()

        file_menu = self._build_file_menu()
        edit_menu = self._build_edit_menu()
        bookmarks_menu = self._build_bookmarks_menu()
        marked_menu = self._build_marked_menu()
        player_menu = self._build_player_menu()
        video_menu = self._build_video_menu()
        recording_menu = self._build_recording_menu()
        help_menu = self._build_help_menu()

        menu_bar.Append(file_menu, _("File"))
        menu_bar.Append(edit_menu, _("Edit"))
        self._bookmarks_menu_index = menu_bar.GetMenuCount()
        menu_bar.Append(bookmarks_menu, _("Bookmarks"))
        self._marked_actions_menu_index = menu_bar.GetMenuCount()
        menu_bar.Append(marked_menu, _("Actions for marked files"))
        menu_bar.Append(player_menu, _("Player"))
        self._video_opts_menu_index = menu_bar.GetMenuCount()
        menu_bar.Append(video_menu, _("Video options"))
        menu_bar.Append(recording_menu, _("Recording"))
        menu_bar.Append(help_menu, _("Help"))

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self._on_exit, self._exit_item)
        if self._jump_menu_map:
            self.Bind(wx.EVT_MENU, self._on_jump_menu)
        if self._seek_step_menu_map:
            self.Bind(wx.EVT_MENU, self._on_seek_step_menu)

        self.set_marked_actions_enabled(False)
        self.set_video_options_enabled(False)
        self.set_recording_state(False, False)

    def _build_file_menu(self):
        menu = wx.Menu()
        self._open_file_item = menu.Append(
            wx.ID_OPEN,
            self._menu_label(_("Open File..."), OPEN_FILE),
        )
        self._open_link_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Open Link..."), OPEN_LINK),
        )
        self._open_yt_link_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Open YouTube Link..."), OPEN_YOUTUBE_LINK),
        )
        self._open_yt_search_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Search YouTube..."), OPEN_YOUTUBE_SEARCH),
        )
        self._open_folder_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Open Folder..."), OPEN_FOLDER),
        )
        self._open_containing_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Open Containing Folder"), OPEN_CONTAINING_FOLDER),
        )
        self._open_file_props_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("File properties..."), OPEN_FILE_PROPERTIES),
        )
        self._open_file_list_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Opened Files..."), OPEN_FILE_LIST),
        )
        self._close_file_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Close File"), CLOSE_FILE),
        )
        self._close_all_files_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Close all files"), CLOSE_ALL_FILES),
        )
        self._test_speakers_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Test speakers"), TEST_SPEAKERS),
        )
        self._settings_item = menu.Append(
            wx.ID_PREFERENCES,
            self._menu_label(_("Preferences..."), OPEN_SETTINGS),
        )
        menu.AppendSeparator()
        self._exit_item = menu.Append(wx.ID_EXIT, _("Exit"))

        self._bind_action_item(self._open_file_item, OPEN_FILE)
        self._bind_action_item(self._open_link_item, OPEN_LINK)
        self._bind_action_item(self._open_yt_link_item, OPEN_YOUTUBE_LINK)
        self._bind_action_item(self._open_yt_search_item, OPEN_YOUTUBE_SEARCH)
        self._bind_action_item(self._open_folder_item, OPEN_FOLDER)
        self._bind_action_item(self._open_containing_item, OPEN_CONTAINING_FOLDER)
        self._bind_action_item(self._open_file_props_item, OPEN_FILE_PROPERTIES)
        self._bind_action_item(self._open_file_list_item, OPEN_FILE_LIST)
        self._bind_action_item(self._close_file_item, CLOSE_FILE)
        self._bind_action_item(self._close_all_files_item, CLOSE_ALL_FILES)
        self._bind_action_item(self._test_speakers_item, TEST_SPEAKERS)
        self._bind_action_item(self._settings_item, OPEN_SETTINGS)
        return menu

    def _build_edit_menu(self):
        menu = wx.Menu()
        self._rename_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Rename..."), RENAME_FILE),
        )
        self._delete_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Delete"), DELETE_FILE),
        )
        self._copy_current_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Copy"), COPY_CURRENT_FILE),
        )
        self._paste_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Paste"), PASTE_FROM_CLIPBOARD),
        )
        menu.AppendSeparator()
        self._mark_current_item = menu.AppendCheckItem(
            wx.ID_ANY,
            self._menu_label(_("Mark Current File"), MARK_CURRENT_FILE),
        )
        self._mark_all_item = menu.AppendCheckItem(
            wx.ID_ANY,
            self._menu_label(_("Mark All Files"), MARK_ALL_FILES),
        )
        self._clear_marked_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Clear Marked Files"), CLEAR_MARKED_FILES),
        )

        self._bind_action_item(self._rename_item, RENAME_FILE)
        self._bind_action_item(self._delete_item, DELETE_FILE)
        self._bind_action_item(self._copy_current_item, COPY_CURRENT_FILE)
        self._bind_action_item(self._paste_item, PASTE_FROM_CLIPBOARD)
        self._bind_action_item(self._mark_current_item, MARK_CURRENT_FILE)
        self._bind_action_item(self._mark_all_item, MARK_ALL_FILES)
        self._bind_action_item(self._clear_marked_item, CLEAR_MARKED_FILES)
        return menu

    def _build_bookmarks_menu(self):
        menu = wx.Menu()
        self._bookmark_add_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Add a new bookmark"), ADD_BOOKMARK),
        )
        self._bookmark_manage_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Manage bookmarks"), MANAGE_BOOKMARKS),
        )
        jumps = wx.Menu()
        self._bookmark_jump_ids = []
        for action_id, slot in sorted(BOOKMARK_JUMPS.items(), key=lambda item: item[1]):
            item = jumps.Append(
                wx.ID_ANY,
                self._menu_label(_("Bookmark {slot}").format(slot=slot), action_id),
            )
            self._bookmark_jump_ids.append(item.GetId())
            self._bind_action_item(item, action_id)
        menu.AppendSubMenu(jumps, _("Jump to bookmark"))

        self._bind_action_item(self._bookmark_add_item, ADD_BOOKMARK)
        self._bind_action_item(self._bookmark_manage_item, MANAGE_BOOKMARKS)
        return menu

    def _build_marked_menu(self):
        menu = wx.Menu()
        self._marked_copy_folder_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("&Copy to folder..."), MARKED_COPY_TO_FOLDER),
        )
        self._marked_move_folder_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("&Move to folder..."), MARKED_MOVE_TO_FOLDER),
        )
        self._marked_copy_clipboard_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Copy to &clipboard"), MARKED_COPY_TO_CLIPBOARD),
        )
        self._marked_delete_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("&Delete"), MARKED_DELETE),
        )
        self._marked_actions_items = (
            self._marked_copy_folder_item,
            self._marked_move_folder_item,
            self._marked_copy_clipboard_item,
            self._marked_delete_item,
        )

        self._bind_action_item(self._marked_copy_folder_item, MARKED_COPY_TO_FOLDER)
        self._bind_action_item(self._marked_move_folder_item, MARKED_MOVE_TO_FOLDER)
        self._bind_action_item(self._marked_copy_clipboard_item, MARKED_COPY_TO_CLIPBOARD)
        self._bind_action_item(self._marked_delete_item, MARKED_DELETE)
        return menu

    def _build_player_menu(self):
        menu = wx.Menu()
        self._play_pause_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Play/Pause"), PLAY_PAUSE),
        )

        speed_menu = wx.Menu()
        self._speed_up_item = speed_menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Increase Speed"), SPEED_UP),
        )
        self._speed_down_item = speed_menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Decrease Speed"), SPEED_DOWN),
        )
        self._reset_speed_item = speed_menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Reset Speed"), RESET_SPEED),
        )
        menu.AppendSubMenu(speed_menu, _("Speed"))
        menu.AppendSeparator()

        self._prev_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Previous"), PREVIOUS_TRACK),
        )
        self._next_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Next"), NEXT_TRACK),
        )
        self._first_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("First File"), GO_FIRST_FILE),
        )
        self._go_to_file_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Go to file..."), GO_TO_FILE),
        )
        self._last_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Last File"), GO_LAST_FILE),
        )
        self._shuffle_item = menu.AppendCheckItem(
            wx.ID_ANY,
            self._menu_label(_("Shuffle"), TOGGLE_SHUFFLE),
        )
        self._repeat_file_item = menu.AppendCheckItem(
            wx.ID_ANY,
            self._menu_label(_("Repeat File"), TOGGLE_REPEAT_FILE),
        )
        self._silence_removal_item = menu.AppendCheckItem(
            wx.ID_ANY,
            self._menu_label(
                _("Enable silence removal filter"),
                TOGGLE_SILENCE_REMOVAL,
            ),
        )

        loop_menu = wx.Menu()
        self._loop_start_item = loop_menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Set A (loop start)"), START_SELECTION),
        )
        self._loop_end_item = loop_menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Set B (loop end)"), END_SELECTION),
        )
        self._loop_clear_item = loop_menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Clear A-B loop"), CLEAR_SELECTION),
        )
        menu.AppendSubMenu(loop_menu, _("A-B loop"))
        menu.AppendSeparator()

        self._rewind_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Rewind"), SEEK_BACKWARD),
        )
        self._forward_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Forward"), SEEK_FORWARD),
        )
        self._start_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Beginning"), SEEK_START),
        )
        self._end_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("End"), SEEK_END),
        )
        self._go_to_time_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Go to time..."), GO_TO_TIME),
        )

        menu.AppendSeparator()
        jump_menu = wx.Menu()
        self._jump_menu_map = {}
        for action_id, percent in sorted(PERCENT_JUMPS.items(), key=lambda item: item[1]):
            item = jump_menu.Append(
                wx.ID_ANY,
                self._menu_label(f"{percent}%", action_id),
            )
            self._jump_menu_map[item.GetId()] = action_id
        menu.AppendSubMenu(jump_menu, _("Jump to Percentage"))

        movement_menu = wx.Menu()
        self._seek_step_menu_map = {}
        step_order = [
            (SEEK_STEP_1, "1"),
            (SEEK_STEP_2, "2"),
            (SEEK_STEP_3, "3"),
            (SEEK_STEP_4, "4"),
            (SEEK_STEP_5, "5"),
            (SEEK_STEP_6, "6"),
            (SEEK_STEP_7, "7"),
            (SEEK_STEP_8, "8"),
            (SEEK_STEP_9, "9"),
            (SEEK_STEP_0, "0"),
            (SEEK_STEP_CUSTOM, "-"),
        ]
        for action_id, key in step_order:
            label = SEEK_STEP_LABELS.get(key, key)
            item = movement_menu.Append(
                wx.ID_ANY,
                self._menu_label(label, action_id),
            )
            self._seek_step_menu_map[item.GetId()] = action_id
        menu.AppendSubMenu(movement_menu, _("Control the clicks movement value"))

        menu.AppendSeparator()
        self._sound_cards_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Sound Cards..."), SOUND_CARDS),
        )

        self._bind_action_item(self._play_pause_item, PLAY_PAUSE)
        self._bind_action_item(self._speed_up_item, SPEED_UP)
        self._bind_action_item(self._speed_down_item, SPEED_DOWN)
        self._bind_action_item(self._reset_speed_item, RESET_SPEED)
        self._bind_action_item(self._prev_item, PREVIOUS_TRACK)
        self._bind_action_item(self._next_item, NEXT_TRACK)
        self._bind_action_item(self._first_item, GO_FIRST_FILE)
        self._bind_action_item(self._go_to_file_item, GO_TO_FILE)
        self._bind_action_item(self._last_item, GO_LAST_FILE)
        self._bind_action_item(self._shuffle_item, TOGGLE_SHUFFLE)
        self._bind_action_item(self._repeat_file_item, TOGGLE_REPEAT_FILE)
        self._bind_action_item(self._silence_removal_item, TOGGLE_SILENCE_REMOVAL)
        self._bind_action_item(self._loop_start_item, START_SELECTION)
        self._bind_action_item(self._loop_end_item, END_SELECTION)
        self._bind_action_item(self._loop_clear_item, CLEAR_SELECTION)
        self._bind_action_item(self._rewind_item, SEEK_BACKWARD)
        self._bind_action_item(self._forward_item, SEEK_FORWARD)
        self._bind_action_item(self._start_item, SEEK_START)
        self._bind_action_item(self._end_item, SEEK_END)
        self._bind_action_item(self._go_to_time_item, GO_TO_TIME)
        self._bind_action_item(self._sound_cards_item, SOUND_CARDS)
        return menu

    def _build_video_menu(self):
        menu = wx.Menu()
        self._video_dl_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Download..."), VIDEO_DOWNLOAD),
        )
        self._video_desc_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Video description..."), VIDEO_DESCRIPTION),
        )
        self._video_copy_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Copy video link"), VIDEO_COPY_LINK),
        )
        self._video_opts_items = (
            self._video_dl_item,
            self._video_desc_item,
            self._video_copy_item,
        )

        self._bind_action_item(self._video_dl_item, VIDEO_DOWNLOAD)
        self._bind_action_item(self._video_desc_item, VIDEO_DESCRIPTION)
        self._bind_action_item(self._video_copy_item, VIDEO_COPY_LINK)
        return menu

    def _build_help_menu(self):
        menu = wx.Menu()
        self._user_guide_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("User Guide"), OPEN_USER_GUIDE),
        )
        self._changes_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("What's new"), OPEN_CHANGES),
        )
        contact_menu = wx.Menu()
        self._contact_email_item = contact_menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Email"), OPEN_CONTACT_EMAIL),
        )
        self._contact_tg_item = contact_menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Telegram"), OPEN_CONTACT_TELEGRAM),
        )
        self._contact_web_item = contact_menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Visit website"), OPEN_CONTACT_WEBSITE),
        )
        menu.AppendSubMenu(contact_menu, _("Contact me"))
        menu.AppendSeparator()
        updates = wx.Menu()
        self._check_updates_item = updates.Append(
            wx.ID_ANY,
            self._menu_label(_("Check for app updates"), CHECK_APP_UPDATES),
        )
        self._update_yt_item = updates.Append(
            wx.ID_ANY,
            self._menu_label(_("Update YouTube components"), UPDATE_YT_COMPONENTS),
        )
        menu.AppendSubMenu(updates, _("Updates"))
        menu.AppendSeparator()
        self._about_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("About"), OPEN_ABOUT),
        )

        self._bind_action_item(self._user_guide_item, OPEN_USER_GUIDE)
        self._bind_action_item(self._changes_item, OPEN_CHANGES)
        self._bind_action_item(self._contact_email_item, OPEN_CONTACT_EMAIL)
        self._bind_action_item(self._contact_tg_item, OPEN_CONTACT_TELEGRAM)
        self._bind_action_item(self._contact_web_item, OPEN_CONTACT_WEBSITE)
        self._bind_action_item(self._check_updates_item, CHECK_APP_UPDATES)
        self._bind_action_item(self._update_yt_item, UPDATE_YT_COMPONENTS)
        self._bind_action_item(self._about_item, OPEN_ABOUT)
        return menu

    def _build_recording_menu(self):
        menu = wx.Menu()
        self._rec_start_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Start recording"), REC_START),
        )
        self._rec_pause_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Pause"), REC_PAUSE),
        )
        self._rec_stop_item = menu.Append(
            wx.ID_ANY,
            self._menu_label(_("Stop"), REC_STOP),
        )
        self._bind_action_item(self._rec_start_item, REC_START)
        self._bind_action_item(self._rec_pause_item, REC_PAUSE)
        self._bind_action_item(self._rec_stop_item, REC_STOP)
        return menu

    def _bind_action_item(self, item, action_id):
        self._menu_action_map[item.GetId()] = action_id
        self.Bind(wx.EVT_MENU, self._on_menu_action, item)

    def _menu_label(self, label, action_id=None):
        text = label
        if action_id:
            shortcut = self._controller.get_shortcuts().get(action_id)
            display = shortcut_to_display(shortcut)
            if display:
                text = f"{text}\t{display}"
        return text

