import json
import os
import shutil

import wx
from gettext import gettext as _
from bookmarks import MarkStore


class BackupRestorePanel(wx.Panel):
    def __init__(self, parent, settings, on_import=None, on_reset=None):
        super().__init__(parent)
        self._settings = settings
        self._on_import = on_import
        self._on_reset = on_reset

        self._export_button = wx.Button(self, label=_("Export settings"))
        self._import_button = wx.Button(self, label=_("Import settings"))
        self._export_marks_button = wx.Button(self, label=_("Export bookmarks"))
        self._import_marks_button = wx.Button(self, label=_("Import bookmarks"))
        self._reset_button = wx.Button(self, label=_("Reset settings"))
        self._open_folder_button = wx.Button(
            self, label=_("Open user settings folder")
        )

        self._export_button.Bind(wx.EVT_BUTTON, self._on_export)
        self._import_button.Bind(wx.EVT_BUTTON, self._on_import_clicked)
        self._export_marks_button.Bind(wx.EVT_BUTTON, self._on_export_marks)
        self._import_marks_button.Bind(wx.EVT_BUTTON, self._on_import_marks)
        self._reset_button.Bind(wx.EVT_BUTTON, self._on_reset_clicked)
        self._open_folder_button.Bind(wx.EVT_BUTTON, self._on_open_folder)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._export_button, 0, wx.ALL | wx.EXPAND, 8)
        sizer.Add(self._import_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        sizer.Add(self._export_marks_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        sizer.Add(self._import_marks_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        sizer.Add(self._reset_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        sizer.Add(self._open_folder_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        self.SetSizer(sizer)

    def apply(self):
        # No persistent fields on this page.
        return

    def get_context_help(self, focused):
        control = focused
        while control is not None:
            if control is self._export_button:
                return _(
                    "Export settings creates a copy of the current settings file."
                )
            if control is self._import_button:
                return _(
                    "Import settings replaces current settings with a selected settings file."
                )
            if control is self._export_marks_button:
                return _(
                    "Export bookmarks creates a copy of the bookmarks JSON file."
                )
            if control is self._import_marks_button:
                return _(
                    "Import bookmarks replaces current bookmarks with a selected bookmarks file."
                )
            if control is self._open_folder_button:
                return _(
                    "Open user settings folder opens the folder where this app stores its configuration."
                )
            if control is self._reset_button:
                return _(
                    "Reset settings restores all preferences to default values."
                )
            if control is self:
                break
            control = control.GetParent()
        return _(
            "Backup and restore settings page. "
            "Use Export settings, Import settings, or Open user settings folder."
        )

    def refresh_from_settings(self):
        return

    def _on_export(self, _event):
        src = self._settings.config_path
        default_dir = os.path.dirname(src)
        default_file = os.path.basename(src)
        with wx.FileDialog(
            self,
            message=_("Export settings"),
            defaultDir=default_dir,
            defaultFile=default_file,
            wildcard=_("INI files (*.ini)|*.ini|All files (*.*)|*.*"),
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            dest = dlg.GetPath()
        try:
            shutil.copy2(src, dest)
        except Exception as exc:
            wx.MessageBox(
                _("Could not export settings.\n{error}").format(error=str(exc)),
                _("Export error"),
                wx.OK | wx.ICON_ERROR,
                parent=self,
            )
            return
        wx.MessageBox(
            _("Settings exported successfully."),
            _("Export settings"),
            wx.OK | wx.ICON_INFORMATION,
            parent=self,
        )

    def _on_import_clicked(self, _event):
        dest = self._settings.config_path
        default_dir = os.path.dirname(dest)
        default_file = os.path.basename(dest)
        with wx.FileDialog(
            self,
            message=_("Import settings"),
            defaultDir=default_dir,
            defaultFile=default_file,
            wildcard=_("INI files (*.ini)|*.ini|All files (*.*)|*.*"),
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            src = dlg.GetPath()
        try:
            if os.path.normcase(os.path.abspath(src)) != os.path.normcase(os.path.abspath(dest)):
                shutil.copy2(src, dest)
            self._settings.load()
            if self._on_import is not None:
                self._on_import()
        except Exception as exc:
            wx.MessageBox(
                _("Could not import settings.\n{error}").format(error=str(exc)),
                _("Import error"),
                wx.OK | wx.ICON_ERROR,
                parent=self,
            )
            return
        wx.MessageBox(
            _("Settings imported successfully."),
            _("Import settings"),
            wx.OK | wx.ICON_INFORMATION,
            parent=self,
        )

    def _on_export_marks(self, _event):
        src = MarkStore(self._settings.config_path).path
        default_dir = os.path.dirname(src)
        default_file = os.path.basename(src)
        with wx.FileDialog(
            self,
            message=_("Export bookmarks"),
            defaultDir=default_dir,
            defaultFile=default_file,
            wildcard=_("JSON files (*.json)|*.json|All files (*.*)|*.*"),
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            dest = dlg.GetPath()
        try:
            if os.path.isfile(src):
                shutil.copy2(src, dest)
            else:
                with open(dest, "w", encoding="utf-8") as handle:
                    json.dump({"version": 1, "files": {}}, handle, ensure_ascii=False, indent=2)
        except Exception as exc:
            wx.MessageBox(
                _("Could not export bookmarks.\n{error}").format(error=str(exc)),
                _("Export error"),
                wx.OK | wx.ICON_ERROR,
                parent=self,
            )
            return
        wx.MessageBox(
            _("Bookmarks exported successfully."),
            _("Export bookmarks"),
            wx.OK | wx.ICON_INFORMATION,
            parent=self,
        )

    def _on_import_marks(self, _event):
        dest = MarkStore(self._settings.config_path).path
        default_dir = os.path.dirname(dest)
        default_file = os.path.basename(dest)
        with wx.FileDialog(
            self,
            message=_("Import bookmarks"),
            defaultDir=default_dir,
            defaultFile=default_file,
            wildcard=_("JSON files (*.json)|*.json|All files (*.*)|*.*"),
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            src = dlg.GetPath()
        try:
            if os.path.normcase(os.path.abspath(src)) != os.path.normcase(os.path.abspath(dest)):
                shutil.copy2(src, dest)
        except Exception as exc:
            wx.MessageBox(
                _("Could not import bookmarks.\n{error}").format(error=str(exc)),
                _("Import error"),
                wx.OK | wx.ICON_ERROR,
                parent=self,
            )
            return
        wx.MessageBox(
            _("Bookmarks imported successfully."),
            _("Import bookmarks"),
            wx.OK | wx.ICON_INFORMATION,
            parent=self,
        )

    def _on_reset_clicked(self, _event):
        result = wx.MessageBox(
            _(
                "Are you sure you want to reset all settings to defaults?\n"
                "This action cannot be undone."
            ),
            _("Reset settings"),
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
            parent=self,
        )
        if result != wx.YES:
            return
        try:
            self._settings.reset_to_defaults()
            if self._on_reset is not None:
                self._on_reset()
        except Exception as exc:
            wx.MessageBox(
                _("Could not reset settings.\n{error}").format(error=str(exc)),
                _("Reset error"),
                wx.OK | wx.ICON_ERROR,
                parent=self,
            )
            return
        wx.MessageBox(
            _("Settings were reset to defaults."),
            _("Reset settings"),
            wx.OK | wx.ICON_INFORMATION,
            parent=self,
        )

    def _on_open_folder(self, _event):
        folder = os.path.dirname(self._settings.config_path)
        try:
            if os.name == "nt":
                os.startfile(folder)
            elif not wx.LaunchDefaultApplication(folder):
                raise RuntimeError("open_failed")
        except Exception:
            wx.MessageBox(
                _("Could not open the settings folder."),
                _("Open folder error"),
                wx.OK | wx.ICON_ERROR,
                parent=self,
            )
