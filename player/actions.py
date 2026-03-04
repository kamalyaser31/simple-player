from dataclasses import dataclass
from typing import Optional

from config.shortcuts import Shortcut


@dataclass(frozen=True)
class Action:
    action_id: str
    label: str
    shortcut: Optional[Shortcut]
    shortcut_secondary: Optional[Shortcut] = None


PLAY_PAUSE = "play_pause"
SEEK_BACKWARD = "seek_backward"
SEEK_FORWARD = "seek_forward"
SEEK_BACKWARD_X2 = "seek_backward_x2"
SEEK_FORWARD_X2 = "seek_forward_x2"
SEEK_BACKWARD_X4 = "seek_backward_x4"
SEEK_FORWARD_X4 = "seek_forward_x4"
SEEK_BACKWARD_X8 = "seek_backward_x8"
SEEK_FORWARD_X8 = "seek_forward_x8"
SEEK_START = "seek_start"
SEEK_END = "seek_end"
VOLUME_UP = "volume_up"
VOLUME_DOWN = "volume_down"
VOLUME_MAXIMIZE = "volume_maximize"
VOLUME_MINIMIZE = "volume_minimize"
ANNOUNCE_VOLUME = "announce_volume"
ANNOUNCE_ELAPSED = "announce_elapsed"
ANNOUNCE_REMAINING = "announce_remaining"
ANNOUNCE_DURATION = "announce_duration"
ANNOUNCE_PERCENT = "announce_percent"
ANNOUNCE_SPEED = "announce_speed"
TOGGLE_VERBOSITY = "toggle_verbosity"
RESET_SPEED = "reset_speed"
OPEN_FILE = "open_file"
OPEN_LINK = "open_link"
OPEN_YOUTUBE_LINK = "open_youtube_link"
OPEN_YOUTUBE_SEARCH = "open_youtube_search"
OPEN_FOLDER = "open_folder"
OPEN_CONTAINING_FOLDER = "open_containing_folder"
OPEN_FILE_LIST = "open_file_list"
OPEN_FILE_PROPERTIES = "open_file_properties"
CLOSE_FILE = "close_file"
CLOSE_ALL_FILES = "close_all_files"
TEST_SPEAKERS = "test_speakers"
OPEN_SETTINGS = "open_settings"
GO_TO_FILE = "go_to_file"
GO_TO_TIME = "go_to_time"
NEXT_TRACK = "next_track"
PREVIOUS_TRACK = "previous_track"
GO_FIRST_FILE = "go_first_file"
GO_LAST_FILE = "go_last_file"
DELETE_FILE = "delete_file"
RENAME_FILE = "rename_file"
COPY_CURRENT_FILE = "copy_current_file"
PASTE_FROM_CLIPBOARD = "paste_from_clipboard"
MARK_CURRENT_FILE = "mark_current_file"
ANNOUNCE_MARKED_COUNT = "announce_marked_count"
MARK_ALL_FILES = "mark_all_files"
CLEAR_MARKED_FILES = "clear_marked_files"
MARKED_COPY_TO_FOLDER = "marked_copy_to_folder"
MARKED_MOVE_TO_FOLDER = "marked_move_to_folder"
MARKED_COPY_TO_CLIPBOARD = "marked_copy_to_clipboard"
MARKED_DELETE = "marked_delete"
ANNOUNCE_FILE_INFO = "announce_file_info"
START_SELECTION = "start_selection"
END_SELECTION = "end_selection"
CLEAR_SELECTION = "clear_selection"
SEEK_STEP_1 = "seek_step_1"
SEEK_STEP_2 = "seek_step_2"
SEEK_STEP_3 = "seek_step_3"
SEEK_STEP_4 = "seek_step_4"
SEEK_STEP_5 = "seek_step_5"
SEEK_STEP_6 = "seek_step_6"
SEEK_STEP_7 = "seek_step_7"
SEEK_STEP_8 = "seek_step_8"
SEEK_STEP_9 = "seek_step_9"
SEEK_STEP_0 = "seek_step_0"
SEEK_STEP_CUSTOM = "seek_step_custom"
SPEED_UP = "speed_up"
SPEED_DOWN = "speed_down"
SOUND_CARDS = "sound_cards"
TOGGLE_SHUFFLE = "toggle_shuffle"
TOGGLE_REPEAT_FILE = "toggle_repeat_file"
TOGGLE_SILENCE_REMOVAL = "toggle_silence_removal"
VIDEO_DOWNLOAD = "video_download"
VIDEO_DESCRIPTION = "video_description"
VIDEO_COPY_LINK = "video_copy_link"
OPEN_USER_GUIDE = "open_user_guide"
OPEN_CHANGES = "open_changes"
OPEN_CONTACT = "open_contact"
OPEN_CONTACT_EMAIL = "open_contact_email"
OPEN_CONTACT_TELEGRAM = "open_contact_telegram"
OPEN_CONTACT_WEBSITE = "open_contact_website"
OPEN_ABOUT = "open_about"
CHECK_APP_UPDATES = "check_app_updates"
UPDATE_YT_COMPONENTS = "update_yt_components"
ADD_BOOKMARK = "add_bookmark"
MANAGE_BOOKMARKS = "manage_bookmarks"
REC_START = "recording_start"
REC_PAUSE = "recording_pause_resume"
REC_STOP = "recording_stop"


ACTIONS = {
    PLAY_PAUSE: Action(PLAY_PAUSE, "Play/Pause", Shortcut("space"), Shortcut("enter")),
    SEEK_BACKWARD: Action(SEEK_BACKWARD, "Seek Backward", Shortcut("left")),
    SEEK_FORWARD: Action(SEEK_FORWARD, "Seek Forward", Shortcut("right")),
    SEEK_BACKWARD_X2: Action(
        SEEK_BACKWARD_X2,
        "Seek Backward x2",
        Shortcut("left", frozenset({"ctrl"})),
    ),
    SEEK_FORWARD_X2: Action(
        SEEK_FORWARD_X2,
        "Seek Forward x2",
        Shortcut("right", frozenset({"ctrl"})),
    ),
    SEEK_BACKWARD_X4: Action(
        SEEK_BACKWARD_X4,
        "Seek Backward x4",
        Shortcut("left", frozenset({"ctrl", "shift"})),
    ),
    SEEK_FORWARD_X4: Action(
        SEEK_FORWARD_X4,
        "Seek Forward x4",
        Shortcut("right", frozenset({"ctrl", "shift"})),
    ),
    SEEK_BACKWARD_X8: Action(
        SEEK_BACKWARD_X8,
        "Seek Backward x8",
        Shortcut("left", frozenset({"shift"})),
    ),
    SEEK_FORWARD_X8: Action(
        SEEK_FORWARD_X8,
        "Seek Forward x8",
        Shortcut("right", frozenset({"shift"})),
    ),
    SEEK_START: Action(SEEK_START, "Seek Start", Shortcut("home")),
    SEEK_END: Action(SEEK_END, "Seek End", Shortcut("end")),
    VOLUME_UP: Action(VOLUME_UP, "Volume Up", Shortcut("up")),
    VOLUME_DOWN: Action(VOLUME_DOWN, "Volume Down", Shortcut("down")),
    VOLUME_MAXIMIZE: Action(
        VOLUME_MAXIMIZE, "Volume Max", Shortcut("up", frozenset({"shift"}))
    ),
    VOLUME_MINIMIZE: Action(
        VOLUME_MINIMIZE, "Volume Min", Shortcut("down", frozenset({"shift"}))
    ),
    ANNOUNCE_VOLUME: Action(ANNOUNCE_VOLUME, "Announce Volume", Shortcut("v")),
    ANNOUNCE_ELAPSED: Action(ANNOUNCE_ELAPSED, "Announce Elapsed", Shortcut("e")),
    ANNOUNCE_REMAINING: Action(ANNOUNCE_REMAINING, "Announce Remaining", Shortcut("r")),
    ANNOUNCE_DURATION: Action(ANNOUNCE_DURATION, "Announce Duration", Shortcut("t")),
    ANNOUNCE_PERCENT: Action(ANNOUNCE_PERCENT, "Announce Percent", Shortcut("p")),
    ANNOUNCE_SPEED: Action(ANNOUNCE_SPEED, "Announce Speed", Shortcut("s")),
    TOGGLE_VERBOSITY: Action(
        TOGGLE_VERBOSITY, "Toggle Verbosity", Shortcut("v", frozenset({"ctrl", "shift"}))
    ),
    RESET_SPEED: Action(RESET_SPEED, "Reset Speed", Shortcut("y", frozenset({"alt"}))),
    OPEN_FILE: Action(OPEN_FILE, "Open File", Shortcut("o", frozenset({"ctrl"}))),
    OPEN_LINK: Action(OPEN_LINK, "Open Link", Shortcut("l", frozenset({"ctrl"}))),
    OPEN_YOUTUBE_LINK: Action(
        OPEN_YOUTUBE_LINK,
        "Open YouTube Link",
        Shortcut("y", frozenset({"ctrl", "shift"})),
    ),
    OPEN_YOUTUBE_SEARCH: Action(
        OPEN_YOUTUBE_SEARCH,
        "Search YouTube",
        Shortcut("y", frozenset({"ctrl"})),
    ),
    VIDEO_DOWNLOAD: Action(
        VIDEO_DOWNLOAD,
        "Video Download",
        Shortcut("d", frozenset({"ctrl"})),
    ),
    VIDEO_DESCRIPTION: Action(
        VIDEO_DESCRIPTION,
        "Video Description",
        Shortcut("d", frozenset({"alt"})),
    ),
    VIDEO_COPY_LINK: Action(
        VIDEO_COPY_LINK,
        "Copy Video Link",
        None,
    ),
    OPEN_USER_GUIDE: Action(
        OPEN_USER_GUIDE,
        "User Guide",
        Shortcut("f1"),
    ),
    OPEN_CHANGES: Action(
        OPEN_CHANGES,
        "What's New",
        None,
    ),
    OPEN_CONTACT: Action(
        OPEN_CONTACT,
        "Contact Me",
        None,
    ),
    OPEN_CONTACT_EMAIL: Action(
        OPEN_CONTACT_EMAIL,
        "Contact: Email",
        None,
    ),
    OPEN_CONTACT_TELEGRAM: Action(
        OPEN_CONTACT_TELEGRAM,
        "Contact: Telegram",
        None,
    ),
    OPEN_CONTACT_WEBSITE: Action(
        OPEN_CONTACT_WEBSITE,
        "Contact: Visit Website",
        None,
    ),
    OPEN_ABOUT: Action(
        OPEN_ABOUT,
        "About",
        None,
    ),
    CHECK_APP_UPDATES: Action(
        CHECK_APP_UPDATES,
        "Check for App Updates",
        None,
    ),
    UPDATE_YT_COMPONENTS: Action(
        UPDATE_YT_COMPONENTS,
        "Update YouTube Components",
        None,
    ),
    ADD_BOOKMARK: Action(
        ADD_BOOKMARK,
        "Add Bookmark",
        Shortcut("m", frozenset({"shift"})),
    ),
    MANAGE_BOOKMARKS: Action(
        MANAGE_BOOKMARKS,
        "Manage Bookmarks",
        Shortcut("m", frozenset({"ctrl", "shift"})),
    ),
    REC_START: Action(
        REC_START,
        "Start Recording",
        Shortcut("f9"),
    ),
    REC_PAUSE: Action(
        REC_PAUSE,
        "Pause/Resume Recording",
        Shortcut("f7"),
    ),
    REC_STOP: Action(
        REC_STOP,
        "Stop Recording",
        Shortcut("f8"),
    ),
    OPEN_FOLDER: Action(
        OPEN_FOLDER, "Open Folder", Shortcut("o", frozenset({"ctrl", "shift"}))
    ),
    OPEN_CONTAINING_FOLDER: Action(
        OPEN_CONTAINING_FOLDER, "Open Containing Folder", Shortcut("f", frozenset({"ctrl"}))
    ),
    OPEN_FILE_PROPERTIES: Action(
        OPEN_FILE_PROPERTIES, "File Properties", Shortcut("enter", frozenset({"alt"}))
    ),
    OPEN_FILE_LIST: Action(OPEN_FILE_LIST, "Opened Files", Shortcut("f2")),
    CLOSE_FILE: Action(CLOSE_FILE, "Close File", Shortcut("w", frozenset({"ctrl"}))),
    CLOSE_ALL_FILES: Action(
        CLOSE_ALL_FILES,
        "Close All Files",
        Shortcut("w", frozenset({"ctrl", "shift"})),
    ),
    TEST_SPEAKERS: Action(
        TEST_SPEAKERS, "Test Speakers", Shortcut("t", frozenset({"ctrl", "shift"}))
    ),
    OPEN_SETTINGS: Action(
        OPEN_SETTINGS, "Settings", Shortcut("p", frozenset({"ctrl"}))
    ),
    GO_TO_FILE: Action(GO_TO_FILE, "Go To File", Shortcut("g", frozenset({"ctrl"}))),
    GO_TO_TIME: Action(
        GO_TO_TIME,
        "Go To Time",
        Shortcut("g", frozenset({"ctrl", "shift"})),
    ),
    NEXT_TRACK: Action(
        NEXT_TRACK,
        "Next Track",
        Shortcut("tab"),
        Shortcut("page_down"),
    ),
    PREVIOUS_TRACK: Action(
        PREVIOUS_TRACK,
        "Previous Track",
        Shortcut("tab", frozenset({"shift"})),
        Shortcut("page_up"),
    ),
    GO_FIRST_FILE: Action(
        GO_FIRST_FILE, "Go to First File", Shortcut("home", frozenset({"ctrl"}))
    ),
    GO_LAST_FILE: Action(
        GO_LAST_FILE, "Go to Last File", Shortcut("end", frozenset({"ctrl"}))
    ),
    DELETE_FILE: Action(
        DELETE_FILE, "Delete File", Shortcut("delete", frozenset({"shift"}))
    ),
    RENAME_FILE: Action(
        RENAME_FILE, "Rename File", Shortcut("f2", frozenset({"shift"}))
    ),
    COPY_CURRENT_FILE: Action(
        COPY_CURRENT_FILE, "Copy Current File", Shortcut("c", frozenset({"ctrl", "shift"}))
    ),
    PASTE_FROM_CLIPBOARD: Action(
        PASTE_FROM_CLIPBOARD, "Paste", Shortcut("v", frozenset({"ctrl"}))
    ),
    MARK_CURRENT_FILE: Action(
        MARK_CURRENT_FILE, "Mark Current File", Shortcut("k", frozenset({"ctrl"}))
    ),
    ANNOUNCE_MARKED_COUNT: Action(
        ANNOUNCE_MARKED_COUNT, "Announce Marked Files Count", Shortcut("k")
    ),
    MARK_ALL_FILES: Action(
        MARK_ALL_FILES, "Mark All Files", Shortcut("a", frozenset({"ctrl"}))
    ),
    CLEAR_MARKED_FILES: Action(
        CLEAR_MARKED_FILES,
        "Clear Marked Files",
        Shortcut("k", frozenset({"ctrl", "shift"})),
    ),
    MARKED_COPY_TO_FOLDER: Action(MARKED_COPY_TO_FOLDER, "Copy to Folder", None),
    MARKED_MOVE_TO_FOLDER: Action(MARKED_MOVE_TO_FOLDER, "Move to Folder", None),
    MARKED_COPY_TO_CLIPBOARD: Action(
        MARKED_COPY_TO_CLIPBOARD, "Copy to Clipboard", None
    ),
    MARKED_DELETE: Action(MARKED_DELETE, "Delete Marked Files", None),
    ANNOUNCE_FILE_INFO: Action(
        ANNOUNCE_FILE_INFO, "Announce File Info", Shortcut("f")
    ),
    START_SELECTION: Action(
        START_SELECTION, "Start Selection", Shortcut("[")
    ),
    END_SELECTION: Action(
        END_SELECTION, "End Selection", Shortcut("]")
    ),
    CLEAR_SELECTION: Action(
        CLEAR_SELECTION, "Clear Selection", Shortcut("backspace")
    ),
    SEEK_STEP_1: Action(SEEK_STEP_1, "Seek Step: 1 Second", Shortcut("1", frozenset({"shift"}))),
    SEEK_STEP_2: Action(SEEK_STEP_2, "Seek Step: 5 Seconds", Shortcut("2", frozenset({"shift"}))),
    SEEK_STEP_3: Action(SEEK_STEP_3, "Seek Step: 1 Minute", Shortcut("3", frozenset({"shift"}))),
    SEEK_STEP_4: Action(SEEK_STEP_4, "Seek Step: 5 Minutes", Shortcut("4", frozenset({"shift"}))),
    SEEK_STEP_5: Action(SEEK_STEP_5, "Seek Step: 10 Minutes", Shortcut("5", frozenset({"shift"}))),
    SEEK_STEP_6: Action(SEEK_STEP_6, "Seek Step: 20 Minutes", Shortcut("6", frozenset({"shift"}))),
    SEEK_STEP_7: Action(SEEK_STEP_7, "Seek Step: 30 Minutes", Shortcut("7", frozenset({"shift"}))),
    SEEK_STEP_8: Action(SEEK_STEP_8, "Seek Step: 40 Minutes", Shortcut("8", frozenset({"shift"}))),
    SEEK_STEP_9: Action(SEEK_STEP_9, "Seek Step: 50 Minutes", Shortcut("9", frozenset({"shift"}))),
    SEEK_STEP_0: Action(SEEK_STEP_0, "Seek Step: 60 Minutes", Shortcut("0", frozenset({"shift"}))),
    SEEK_STEP_CUSTOM: Action(SEEK_STEP_CUSTOM, "Seek Step: Custom", Shortcut("-", frozenset({"shift"}))),
    SPEED_UP: Action(SPEED_UP, "Speed Up", Shortcut("up", frozenset({"ctrl"}))),
    SPEED_DOWN: Action(SPEED_DOWN, "Speed Down", Shortcut("down", frozenset({"ctrl"}))),
    SOUND_CARDS: Action(
        SOUND_CARDS, "Sound Cards", Shortcut("a", frozenset({"ctrl", "shift"}))
    ),
    TOGGLE_SHUFFLE: Action(
        TOGGLE_SHUFFLE, "Shuffle", Shortcut("z", frozenset({"ctrl"}))
    ),
    TOGGLE_REPEAT_FILE: Action(
        TOGGLE_REPEAT_FILE, "Repeat File", Shortcut("r", frozenset({"ctrl"}))
    ),
    TOGGLE_SILENCE_REMOVAL: Action(
        TOGGLE_SILENCE_REMOVAL, "Silence Removal", Shortcut("m", frozenset({"ctrl"}))
    ),
}

GLOBAL_SHORTCUT_ACTIONS = {
    PLAY_PAUSE: Action(
        PLAY_PAUSE, "Play/Pause", Shortcut("space", frozenset({"win", "alt"}))
    ),
    SEEK_BACKWARD: Action(
        SEEK_BACKWARD, "Seek Backward", Shortcut("left", frozenset({"win", "alt"}))
    ),
    SEEK_FORWARD: Action(
        SEEK_FORWARD, "Seek Forward", Shortcut("right", frozenset({"win", "alt"}))
    ),
    VOLUME_UP: Action(
        VOLUME_UP, "Volume Up", Shortcut("up", frozenset({"win", "alt"}))
    ),
    VOLUME_DOWN: Action(
        VOLUME_DOWN, "Volume Down", Shortcut("down", frozenset({"win", "alt"}))
    ),
    NEXT_TRACK: Action(
        NEXT_TRACK,
        "Next Track",
        Shortcut("page_down", frozenset({"win", "alt"})),
    ),
    PREVIOUS_TRACK: Action(
        PREVIOUS_TRACK,
        "Previous Track",
        Shortcut("page_up", frozenset({"win", "alt"})),
    ),
}

BOOKMARK_JUMPS = {}
for slot in range(1, 11):
    key = "0" if slot == 10 else str(slot)
    action_id = f"bookmark_jump_{slot}"
    ACTIONS[action_id] = Action(
        action_id,
        f"Jump to Bookmark {slot}",
        Shortcut(key, frozenset({"alt"})),
    )
    BOOKMARK_JUMPS[action_id] = slot

PERCENT_JUMPS = {}
for digit in range(10):
    base_percent = 100 if digit == 0 else digit * 10
    action_id = f"jump_percent_{base_percent}"
    ACTIONS[action_id] = Action(
        action_id,
        f"Jump to {base_percent}%",
        Shortcut(str(digit), frozenset({"ctrl"})),
    )
    PERCENT_JUMPS[action_id] = base_percent

    shift_percent = min(100, base_percent + 5)
    shift_action_id = f"jump_percent_{base_percent}_shift"
    ACTIONS[shift_action_id] = Action(
        shift_action_id,
        f"Jump to {shift_percent}%",
        Shortcut(str(digit), frozenset({"ctrl", "shift"})),
    )
    PERCENT_JUMPS[shift_action_id] = shift_percent
