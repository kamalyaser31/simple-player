import wx
from gettext import gettext as _

import speech
from actions import ACTIONS, GLOBAL_SHORTCUT_ACTIONS
from ui.audio_settings import AudioSettings
from ui.prefs.backup import BackupRestorePanel
from ui.prefs.general import GeneralSettingsPanel
from ui.prefs.recording import RecordingSettingsPanel
from ui.prefs.youtube import YouTubeSettingsPanel
from ui.shortcut_settings import ShortcutSettings
from ui.silence_removal import SilenceRemovalSettings


class SettingsDialog(wx.Dialog):
    def __init__(self, parent, settings, on_download_youtube_components=None):
        super().__init__(
            parent,
            title=_("Preferences"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._settings = settings
        self._tree = wx.TreeCtrl(
            self, style=wx.TR_HIDE_ROOT | wx.TR_DEFAULT_STYLE | wx.TR_HAS_BUTTONS
        )
        self._book = wx.Panel(self)
        self._book_sizer = wx.BoxSizer(wx.VERTICAL)
        self._book.SetSizer(self._book_sizer)
        self._pages = {}
        self._panels = []
        self._current_panel = None

        root = self._tree.AddRoot("root")
        general_item = self._tree.AppendItem(root, _("General"))
        self._general_panel = GeneralSettingsPanel(self._book, settings)
        self._book_sizer.Add(self._general_panel, 1, wx.EXPAND)
        self._pages[general_item] = self._general_panel
        self._panels.append(self._general_panel)
        self._current_panel = self._general_panel

        backup_item = self._tree.AppendItem(root, _("Backup and restore"))
        self._backup_panel = BackupRestorePanel(
            self._book,
            settings,
            on_import=self._refresh_panels_from_settings,
        )
        self._book_sizer.Add(self._backup_panel, 1, wx.EXPAND)
        self._backup_panel.Hide()
        self._pages[backup_item] = self._backup_panel
        self._panels.append(self._backup_panel)

        audio_item = self._tree.AppendItem(root, _("Audio"))
        silence_removal_item = self._tree.AppendItem(root, _("Silence removal"))
        self._audio_panel = AudioSettings(self._book, settings)
        self._book_sizer.Add(self._audio_panel, 1, wx.EXPAND)
        self._audio_panel.Hide()
        self._pages[audio_item] = self._audio_panel
        self._panels.append(self._audio_panel)

        self._silence_removal_panel = SilenceRemovalSettings(self._book, settings)
        self._book_sizer.Add(self._silence_removal_panel, 1, wx.EXPAND)
        self._silence_removal_panel.Hide()
        self._pages[silence_removal_item] = self._silence_removal_panel
        self._panels.append(self._silence_removal_panel)

        recording_item = self._tree.AppendItem(root, _("Recording"))
        self._recording_panel = RecordingSettingsPanel(self._book, settings)
        self._book_sizer.Add(self._recording_panel, 1, wx.EXPAND)
        self._recording_panel.Hide()
        self._pages[recording_item] = self._recording_panel
        self._panels.append(self._recording_panel)

        youtube_item = self._tree.AppendItem(root, _("YouTube"))
        self._youtube_panel = YouTubeSettingsPanel(
            self._book,
            settings,
            on_download_components=on_download_youtube_components,
        )
        self._book_sizer.Add(self._youtube_panel, 1, wx.EXPAND)
        self._youtube_panel.Hide()
        self._pages[youtube_item] = self._youtube_panel
        self._panels.append(self._youtube_panel)

        shortcuts_item = self._tree.AppendItem(root, _("Keyboard Shortcuts"))
        global_shortcuts_item = self._tree.AppendItem(root, _("Global shortcuts"))
        self._shortcuts_panel = ShortcutSettings(
            self._book,
            settings,
            action_definitions=ACTIONS,
            get_overrides=settings.get_shortcut_overrides,
            set_overrides=settings.set_shortcut_overrides,
            get_secondary_overrides=settings.get_secondary_shortcut_overrides,
            set_secondary_overrides=settings.set_secondary_shortcut_overrides,
            title=_("Local Shortcuts"),
        )
        self._book_sizer.Add(self._shortcuts_panel, 1, wx.EXPAND)
        self._shortcuts_panel.Hide()
        self._pages[shortcuts_item] = self._shortcuts_panel
        self._panels.append(self._shortcuts_panel)

        self._global_shortcuts_panel = ShortcutSettings(
            self._book,
            settings,
            action_definitions=GLOBAL_SHORTCUT_ACTIONS,
            get_overrides=settings.get_global_shortcut_overrides,
            set_overrides=settings.set_global_shortcut_overrides,
            title=_("Global Shortcuts"),
            capture_mode="pynput",
        )
        self._book_sizer.Add(self._global_shortcuts_panel, 1, wx.EXPAND)
        self._global_shortcuts_panel.Hide()
        self._pages[global_shortcuts_item] = self._global_shortcuts_panel
        self._panels.append(self._global_shortcuts_panel)

        self._tree.SelectItem(general_item)
        self._tree.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_tree_changed)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

        body_sizer = wx.BoxSizer(wx.HORIZONTAL)
        body_sizer.Add(self._tree, 0, wx.EXPAND | wx.ALL, 8)
        body_sizer.Add(self._book, 1, wx.EXPAND | wx.ALL, 8)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(body_sizer, 1, wx.EXPAND)
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        if buttons:
            main_sizer.Add(buttons, 0, wx.EXPAND | wx.ALL, 8)
        self.SetSizerAndFit(main_sizer)
        self.SetMinSize((420, 260))

        ok_button = self.FindWindowById(wx.ID_OK, self)
        if ok_button is not None:
            ok_button.Bind(wx.EVT_BUTTON, self._on_ok)

    def apply(self):
        for panel in self._panels:
            panel.apply()

    def _on_ok(self, _event):
        for panel in self._panels:
            if not hasattr(panel, "validate_inputs"):
                continue
            try:
                err = str(panel.validate_inputs() or "").strip()
            except Exception:
                err = ""
            if err:
                wx.MessageBox(
                    err,
                    _("Preferences"),
                    wx.OK | wx.ICON_ERROR,
                    parent=self,
                )
                return
        self.EndModal(wx.ID_OK)

    def _on_tree_changed(self, event):
        item = event.GetItem()
        panel = self._pages.get(item)
        if panel is not None and panel is not self._current_panel:
            if self._current_panel is not None:
                self._current_panel.Hide()
            panel.Show()
            self._current_panel = panel
            self._book.Layout()
        event.Skip()

    def _on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_F1:
            self._announce_context_help()
            return
        event.Skip()

    def _announce_context_help(self):
        focused = wx.Window.FindFocus()
        if focused is self._tree:
            speech.speak(
                _(
                    "Settings categories tree. "
                    "Use up and down arrows to choose a category like General or Audio."
                )
            )
            return
        message = None
        panel = self._current_panel
        if panel is not None and hasattr(panel, "get_context_help"):
            try:
                message = panel.get_context_help(focused)
            except Exception:
                message = None
        if not message:
            message = _(
                "No detailed help is available for this control."
            )
        speech.speak(message)

    def _refresh_panels_from_settings(self):
        for panel in self._panels:
            if hasattr(panel, "refresh_from_settings"):
                try:
                    panel.refresh_from_settings()
                except Exception:
                    continue
