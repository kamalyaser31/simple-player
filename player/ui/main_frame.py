import wx
from gettext import gettext as _

from actions import NEXT_TRACK, PLAY_PAUSE, PREVIOUS_TRACK, SEEK_BACKWARD, SEEK_FORWARD
from ui.custom_controls import CustomButton
from ui.mainwin.events import MainFrameEventsMixin
from ui.mainwin.menu import MainFrameMenuMixin
from ui.mainwin.state import MainFrameStateMixin


class MainFrame(MainFrameMenuMixin, MainFrameStateMixin, MainFrameEventsMixin, wx.Frame):
    def __init__(self, controller, title):
        super().__init__(None, title=title, size=(420, 160))
        self._controller = controller
        self._action_id_map = {}
        self._menu_action_map = {}
        self._accelerator_bound = False
        self._jump_menu_map = {}
        self._bookmark_jump_ids = []
        self._seek_step_menu_map = {}
        self._bookmarks_menu_index = -1
        self._bookmarks_enabled = False
        self._marked_actions_items = ()
        self._marked_actions_menu_index = -1
        self._has_marked_files = False
        self._file_loaded = False
        self._file_props_enabled = False
        self._local_file_actions_enabled = False
        self._video_opts_items = ()
        self._video_opts_menu_index = -1
        self._video_opts_enabled = False
        self._recording_running = False
        self._recording_paused = False

        self._build_menu()
        self._build_ui()
        self._build_shortcuts()
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
        self.set_file_loaded(False)

    def set_controller(self, controller):
        self._controller = controller

    def _build_ui(self):
        self._prev_button = CustomButton(self, -1, _("Previous"))
        self._rewind_button = CustomButton(self, -1, _("Rewind"))
        self._play_button = CustomButton(self, -1, _("Play"))
        self._forward_button = CustomButton(self, -1, _("Forward"))
        self._next_button = CustomButton(self, -1, _("Next"))

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Insert(0, self._prev_button, 0, wx.ALL, 5)
        button_sizer.Add(self._rewind_button, 0, wx.ALL, 5)
        button_sizer.Add(self._play_button, 0, wx.ALL, 5)
        button_sizer.Add(self._forward_button, 0, wx.ALL, 5)
        button_sizer.Add(self._next_button, 0, wx.ALL, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 15)
        self.SetSizer(sizer)
        self.Fit()

        self._prev_button.Bind(
            wx.EVT_BUTTON,
            lambda _e: self._controller.handle_action(PREVIOUS_TRACK),
        )
        self._rewind_button.Bind(
            wx.EVT_BUTTON,
            lambda _e: self._controller.handle_action(SEEK_BACKWARD),
        )
        self._play_button.Bind(
            wx.EVT_BUTTON,
            lambda _e: self._controller.handle_action(PLAY_PAUSE),
        )
        self._forward_button.Bind(
            wx.EVT_BUTTON,
            lambda _e: self._controller.handle_action(SEEK_FORWARD),
        )
        self._next_button.Bind(
            wx.EVT_BUTTON,
            lambda _e: self._controller.handle_action(NEXT_TRACK),
        )

    def get_video_window_handle(self):
        return int(self.GetHandle())
