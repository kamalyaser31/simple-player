import wx
from gettext import gettext as _

from config.file_associations import (
    register_file_associations,
    unregister_file_associations,
)
from config.localization import available_languages, language_name


class GeneralSettingsPanel(wx.Panel):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self._settings = settings
        self._lang_label = wx.StaticText(self, label=_("Language"))
        lang_rows = []
        for code in available_languages():
            lang_rows.append((code, language_name(code)))
        lang_rows.sort(key=lambda row: row[1].lower())
        self._lang_values = ["system"] + [row[0] for row in lang_rows]
        self._lang_labels = [_("System default")] + [row[1] for row in lang_rows]
        self._lang_choice = wx.Choice(self, choices=self._lang_labels)
        self._set_language_selection(self._settings.get_ui_language())

        self._remember_checkbox = wx.CheckBox(
            self, label=_("Remember last file position")
        )
        self._remember_checkbox.SetValue(self._settings.get_remember_position())
        self._speak_nav_checkbox = wx.CheckBox(
            self, label=_("Speak file name when navigating (Previous/Next)")
        )
        self._speak_nav_checkbox.SetValue(self._settings.get_speak_file_on_nav())
        self._check_updates_checkbox = wx.CheckBox(
            self,
            label=_("Check for app updates on startup"),
        )
        self._check_updates_checkbox.SetValue(self._settings.get_check_app_updates())
        self._save_on_close_checkbox = wx.CheckBox(
            self,
            label=_("Save settings on close"),
        )
        self._save_on_close_checkbox.SetValue(self._settings.get_save_on_close())
        self._verbosity_labels = [
            _("Beginner"),
            _("Advanced"),
        ]
        self._verbosity_values = [
            "beginner",
            "advanced",
        ]
        self._verbosity_label = wx.StaticText(self, label=_("Verbosity"))
        self._verbosity_choice = wx.Choice(self, choices=self._verbosity_labels)
        current = self._settings.get_verbosity()
        try:
            index = self._verbosity_values.index(current)
        except ValueError:
            index = 0
        self._verbosity_choice.SetSelection(index)

        self._open_with_files_labels = [
            _("Open the file only"),
            _("Open the file and the main folder files"),
            _("Open the file with the main and subfolder files"),
        ]
        self._open_with_files_values = [
            "file_only",
            "main_folder",
            "main_and_subfolders",
        ]
        self._open_with_files_label = wx.StaticText(
            self, label=_("What would you like to open with files?")
        )
        self._open_with_files_choice = wx.Choice(
            self, choices=self._open_with_files_labels
        )
        current_open_with = self._settings.get_open_with_files_mode()
        try:
            open_with_index = self._open_with_files_values.index(current_open_with)
        except ValueError:
            open_with_index = 0
        self._open_with_files_choice.SetSelection(open_with_index)

        self._register_extensions_button = wx.Button(
            self, label=_("Register file extensions")
        )
        self._unregister_extensions_button = wx.Button(
            self, label=_("Unregister file extensions")
        )
        self._register_extensions_button.Bind(
            wx.EVT_BUTTON, self._on_register_file_extensions
        )
        self._unregister_extensions_button.Bind(
            wx.EVT_BUTTON, self._on_unregister_file_extensions
        )

        sizer = wx.BoxSizer(wx.VERTICAL)
        language_sizer = wx.BoxSizer(wx.VERTICAL)
        language_sizer.Add(self._lang_label, 0, wx.BOTTOM, 4)
        language_sizer.Add(self._lang_choice, 0, wx.EXPAND)
        sizer.Add(language_sizer, 0, wx.ALL | wx.EXPAND, 8)
        sizer.Add(self._remember_checkbox, 0, wx.ALL, 8)
        sizer.Add(self._speak_nav_checkbox, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        sizer.Add(self._check_updates_checkbox, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        sizer.Add(self._save_on_close_checkbox, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        verbosity_sizer = wx.BoxSizer(wx.VERTICAL)
        verbosity_sizer.Add(self._verbosity_label, 0, wx.BOTTOM, 4)
        verbosity_sizer.Add(self._verbosity_choice, 0, wx.EXPAND)
        sizer.Add(verbosity_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        open_with_sizer = wx.BoxSizer(wx.VERTICAL)
        open_with_sizer.Add(self._open_with_files_label, 0, wx.BOTTOM, 4)
        open_with_sizer.Add(self._open_with_files_choice, 0, wx.EXPAND)
        sizer.Add(open_with_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        association_buttons = wx.BoxSizer(wx.HORIZONTAL)
        association_buttons.Add(self._register_extensions_button, 0, wx.RIGHT, 6)
        association_buttons.Add(self._unregister_extensions_button, 0)
        sizer.Add(
            association_buttons,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM,
            8,
        )
        self.SetSizer(sizer)
        self._help_map = {
            self._lang_choice: self._help_language,
            self._remember_checkbox: self._help_remember_position,
            self._speak_nav_checkbox: self._help_speak_nav,
            self._check_updates_checkbox: self._help_check_updates,
            self._save_on_close_checkbox: self._help_save_on_close,
            self._verbosity_choice: self._help_verbosity,
            self._open_with_files_choice: self._help_open_with_files,
            self._register_extensions_button: self._help_register_extensions,
            self._unregister_extensions_button: self._help_unregister_extensions,
        }

    def apply(self):
        lang_selection = self._lang_choice.GetSelection()
        if lang_selection == wx.NOT_FOUND:
            lang_selection = 0
        self._settings.set_ui_language(self._lang_values[lang_selection])
        self._settings.set_remember_position(self._remember_checkbox.GetValue())
        self._settings.set_speak_file_on_nav(self._speak_nav_checkbox.GetValue())
        self._settings.set_check_app_updates(self._check_updates_checkbox.GetValue())
        self._settings.set_save_on_close(self._save_on_close_checkbox.GetValue())
        selection = self._verbosity_choice.GetSelection()
        if selection == wx.NOT_FOUND:
            selection = 0
        self._settings.set_verbosity(self._verbosity_values[selection])
        open_with_selection = self._open_with_files_choice.GetSelection()
        if open_with_selection == wx.NOT_FOUND:
            open_with_selection = 0
        self._settings.set_open_with_files_mode(
            self._open_with_files_values[open_with_selection]
        )

    def refresh_from_settings(self):
        self._set_language_selection(self._settings.get_ui_language())
        self._remember_checkbox.SetValue(self._settings.get_remember_position())
        self._speak_nav_checkbox.SetValue(self._settings.get_speak_file_on_nav())
        self._check_updates_checkbox.SetValue(self._settings.get_check_app_updates())
        self._save_on_close_checkbox.SetValue(self._settings.get_save_on_close())
        current = self._settings.get_verbosity()
        try:
            index = self._verbosity_values.index(current)
        except ValueError:
            index = 0
        self._verbosity_choice.SetSelection(index)
        current_open_with = self._settings.get_open_with_files_mode()
        try:
            open_with_index = self._open_with_files_values.index(current_open_with)
        except ValueError:
            open_with_index = 0
        self._open_with_files_choice.SetSelection(open_with_index)

    def get_context_help(self, focused):
        control = focused
        while control is not None:
            if control in self._help_map:
                return self._help_map[control]()
            if control is self:
                break
            control = control.GetParent()
        return _(
            "General settings. Use Tab to move between controls. "
            "Press F1 on a specific control to hear detailed help."
        )

    def _help_remember_position(self):
        return _(
            "Remember last file position. "
            "When enabled, the player saves the current file and playback time on exit, "
            "then restores that position next time. "
            "When disabled, the player starts fresh each launch."
        )

    def _help_speak_nav(self):
        return _(
            "Speak file name when navigating. "
            "When enabled, the player will announce the name of the new file when you move to the previous or next track. "
            "This is helpful for identifying files without manually requesting file information."
        )

    def _help_language(self):
        return _(
            "Application language. "
            "System default follows your OS language. "
            "Choosing a specific language applies it on next app start."
        )

    def _help_verbosity(self):
        return _(
            "Verbosity controls speech detail. "
            "Beginner gives clearer full messages. "
            "Advanced gives shorter, compact announcements. "
            "Possible values: Beginner or Advanced."
        )

    def _help_check_updates(self):
        return _(
            "Check for app updates on startup. "
            "When enabled, the app checks online update metadata at launch and prompts when a newer version is available."
        )

    def _help_save_on_close(self):
        return _(
            "Save settings on close. "
            "When enabled, current settings are written when the app closes. "
            "When disabled, closing the app does not save session changes such as volume, speed, or other setting updates."
        )

    def _help_open_with_files(self):
        return _(
            "Open with files behavior controls what happens when you open a single file. "
            "Open the file only loads just that file. "
            "Open the file and the main folder files loads all supported files in the same folder. "
            "Open the file with the main and subfolder files scans the folder recursively and loads files from subfolders too."
        )

    def _help_register_extensions(self):
        return _(
            "Register file extensions writes Windows registry entries for supported media types. "
            "This lets files open with this app from Explorer and Open With. "
            "On modern Windows, default app choice can still require user confirmation in system Default apps settings."
        )

    def _help_unregister_extensions(self):
        return _(
            "Unregister file extensions removes registry entries created by this app for media associations. "
            "This does not delete your media files. "
            "Windows may still keep separate user default selections managed by system settings."
        )

    def _on_register_file_extensions(self, _event):
        ok, error = register_file_associations()
        if ok:
            wx.MessageBox(
                _("File extensions registered successfully."),
                _("Registration"),
                wx.OK | wx.ICON_INFORMATION,
                parent=self,
            )
        else:
            wx.MessageBox(
                _("Could not register file extensions.\n{error}").format(error=error),
                _("Registration Error"),
                wx.OK | wx.ICON_ERROR,
                parent=self,
            )

    def _on_unregister_file_extensions(self, _event):
        ok, error = unregister_file_associations()
        if ok:
            wx.MessageBox(
                _("File extensions unregistered successfully."),
                _("Unregister"),
                wx.OK | wx.ICON_INFORMATION,
                parent=self,
            )
        else:
            wx.MessageBox(
                _("Could not unregister file extensions.\n{error}").format(error=error),
                _("Unregister Error"),
                wx.OK | wx.ICON_ERROR,
                parent=self,
            )

    def _set_language_selection(self, current_code):
        code = str(current_code or "system").strip()
        try:
            idx = self._lang_values.index(code)
        except ValueError:
            idx = 0
        self._lang_choice.SetSelection(idx)
