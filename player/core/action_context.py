import time

import speech


class ActionContext:
    def __init__(self, player, settings, marks=None, file_pos=None, favs=None):
        self.player = player
        self.settings = settings
        self.marks = marks
        self.file_pos = file_pos
        self.favs = favs
        self.frame = None
        self.selection_start = None
        self.selection_end = None
        self.selection_path = None
        self.file_info_press_count = 0
        self.file_info_last_press = 0.0
        self.yt_pl = None
        self.yt_now = None

    def set_frame(self, frame):
        self.frame = frame

    def is_advanced(self):
        return self.settings.get_verbosity() == "advanced"

    def speak(self, beginner_text, advanced_text=None):
        if self.is_advanced():
            speech.speak(advanced_text or beginner_text)
        else:
            speech.speak(beginner_text)

    def announce_volume_value(self, volume, beginner_template):
        if self.is_advanced():
            speech.speak(f"{int(volume)}%")
        else:
            speech.speak(beginner_template.format(volume=int(volume)))

    def set_playing(self, is_playing):
        if self.frame is not None:
            self.frame.set_playing(is_playing)

    def set_file_loaded(self, loaded):
        if self.frame is not None:
            self.frame.set_file_loaded(loaded)

    def reset_selection(self, clear_loop=True):
        self.selection_start = None
        self.selection_end = None
        self.selection_path = None
        if clear_loop:
            self.player.clear_loop()

    def should_reset_file_info(self):
        return time.time() - self.file_info_last_press > 0.3
