import wx
from gettext import gettext as _
from pynput import keyboard

from actions import ACTIONS
from config.shortcut_utils import shortcut_from_event, shortcut_to_display, shortcuts_equal
from config.shortcuts import Shortcut


class ShortcutCaptureDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(
            parent,
            title=_("Set Shortcut"),
            style=wx.DEFAULT_DIALOG_STYLE,
        )
        self.shortcut = None
        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(
            self, label=_("Press the desired shortcut. Escape cancels.")
        )
        sizer.Add(label, 0, wx.ALL, 10)
        self.SetSizerAndFit(sizer)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_key)
        self.CentreOnParent()

    def _on_key(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
            return
        shortcut = shortcut_from_event(event)
        if not shortcut:
            return
        self.shortcut = shortcut
        self.EndModal(wx.ID_OK)


_MODIFIER_KEYS = {
    keyboard.Key.ctrl: "ctrl",
    keyboard.Key.ctrl_l: "ctrl",
    keyboard.Key.ctrl_r: "ctrl",
    keyboard.Key.shift: "shift",
    keyboard.Key.shift_l: "shift",
    keyboard.Key.shift_r: "shift",
    keyboard.Key.alt: "alt",
    keyboard.Key.alt_l: "alt",
    keyboard.Key.alt_r: "alt",
    keyboard.Key.cmd: "win",
    keyboard.Key.cmd_l: "win",
    keyboard.Key.cmd_r: "win",
}

_SPECIAL_KEYS = {
    keyboard.Key.space: "space",
    keyboard.Key.left: "left",
    keyboard.Key.right: "right",
    keyboard.Key.up: "up",
    keyboard.Key.down: "down",
    keyboard.Key.page_up: "page_up",
    keyboard.Key.page_down: "page_down",
    keyboard.Key.home: "home",
    keyboard.Key.end: "end",
    keyboard.Key.delete: "delete",
    keyboard.Key.backspace: "backspace",
}


class GlobalShortcutCaptureDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(
            parent,
            title=_("Set Global Shortcut"),
            style=wx.DEFAULT_DIALOG_STYLE,
        )
        self.shortcut = None
        self._modifiers = set()
        self._listener = None
        self._finished = False

        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(
            self,
            label=_("Press the desired global shortcut. Escape cancels."),
        )
        sizer.Add(label, 0, wx.ALL, 10)
        self.SetSizerAndFit(sizer)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.CentreOnParent()
        self._start_listener()

    def _start_listener(self):
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            suppress=False,
        )
        self._listener.start()

    def _on_press(self, key):
        modifier = _MODIFIER_KEYS.get(key)
        if modifier is not None:
            self._modifiers.add(modifier)
            return

        token = _pynput_key_token(key)
        if not token:
            return
        if token == "esc":
            wx.CallAfter(self._finish_cancel)
            return

        shortcut = Shortcut(token, frozenset(self._modifiers))
        wx.CallAfter(self._finish_ok, shortcut)

    def _on_release(self, key):
        modifier = _MODIFIER_KEYS.get(key)
        if modifier is not None:
            self._modifiers.discard(modifier)

    def _finish_ok(self, shortcut):
        if self._finished:
            return
        self._finished = True
        self.shortcut = shortcut
        self._stop_listener()
        self.EndModal(wx.ID_OK)

    def _finish_cancel(self):
        if self._finished:
            return
        self._finished = True
        self._stop_listener()
        self.EndModal(wx.ID_CANCEL)

    def _on_close(self, _event):
        self._finish_cancel()

    def _stop_listener(self):
        listener = self._listener
        self._listener = None
        if listener is not None:
            try:
                listener.stop()
            except Exception:
                pass


def _pynput_key_token(key):
    if key in _SPECIAL_KEYS:
        return _SPECIAL_KEYS[key]
    if key == keyboard.Key.esc:
        return "esc"
    if isinstance(key, keyboard.KeyCode):
        if key.char:
            return key.char.lower()
        if key.vk is not None and 112 <= key.vk <= 135:
            return f"f{key.vk - 111}"
    return ""


class ShortcutSettings(wx.Panel):
    def __init__(
        self,
        parent,
        settings,
        action_definitions=None,
        get_overrides=None,
        set_overrides=None,
        get_secondary_overrides=None,
        set_secondary_overrides=None,
        title=None,
        capture_mode="wx",
    ):
        super().__init__(parent)
        self._settings = settings
        self._action_definitions = action_definitions or ACTIONS
        self._actions = list(self._action_definitions.items())
        self._get_overrides = get_overrides or self._settings.get_shortcut_overrides
        self._set_overrides = set_overrides or self._settings.set_shortcut_overrides
        self._get_secondary_overrides = (
            get_secondary_overrides
            or (lambda: {})
        )
        self._set_secondary_overrides = (
            set_secondary_overrides
            or (lambda _overrides: None)
        )
        self._overrides = dict(self._get_overrides())
        self._secondary_overrides = dict(self._get_secondary_overrides())
        self._capture_mode = capture_mode
        self._has_secondary_actions = any(
            action.shortcut_secondary is not None for _, action in self._actions
        )

        self._label = wx.StaticText(self, label=title or _("Keyboard Shortcuts"))
        self._list = wx.ListCtrl(
            self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN
        )
        self._list.InsertColumn(0, _("Action"))
        self._list.InsertColumn(1, _("Primary Shortcut"))
        if self._has_secondary_actions:
            self._list.InsertColumn(2, _("Secondary Shortcut"))
        self._edit_button = wx.Button(self, label=_("Edit Primary Shortcut"))
        self._edit_secondary_button = None
        if self._has_secondary_actions:
            self._edit_secondary_button = wx.Button(
                self,
                label=_("Edit Secondary Shortcut"),
            )
        self._reset_button = wx.Button(self, label=_("Reset to Defaults"))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        sizer.Add(self._list, 1, wx.ALL | wx.EXPAND, 8)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self._edit_button, 0, wx.RIGHT, 6)
        if self._edit_secondary_button is not None:
            button_sizer.Add(self._edit_secondary_button, 0, wx.RIGHT, 6)
        button_sizer.Add(self._reset_button, 0)
        sizer.Add(button_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        self.SetSizer(sizer)

        self._list.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selection_changed)
        self._list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_selection_changed)
        self._edit_button.Bind(wx.EVT_BUTTON, self._on_edit_primary)
        if self._edit_secondary_button is not None:
            self._edit_secondary_button.Bind(wx.EVT_BUTTON, self._on_edit_secondary)
        self._reset_button.Bind(wx.EVT_BUTTON, self._on_reset)

        self._refresh_list()
        self._update_buttons()

    def apply(self):
        overrides_to_save = {}
        for action_id, action in self._actions:
            override = self._overrides.get(action_id)
            if override is None:
                continue
            if shortcuts_equal(override, action.shortcut):
                continue
            overrides_to_save[action_id] = override
        self._set_overrides(overrides_to_save)
        secondary_overrides_to_save = {}
        for action_id, action in self._actions:
            if action.shortcut_secondary is None:
                continue
            override = self._secondary_overrides.get(action_id)
            if override is None:
                continue
            if shortcuts_equal(override, action.shortcut_secondary):
                continue
            secondary_overrides_to_save[action_id] = override
        self._set_secondary_overrides(secondary_overrides_to_save)

    def refresh_from_settings(self):
        self._overrides = dict(self._get_overrides())
        self._secondary_overrides = dict(self._get_secondary_overrides())
        self._refresh_list()

    def _on_selection_changed(self, _event):
        self._update_buttons()

    def _update_buttons(self):
        index = self._list.GetFirstSelected()
        self._edit_button.Enable(index != -1)
        if self._edit_secondary_button is not None:
            enabled = index != -1 and self._supports_secondary(self._actions[index][1])
            self._edit_secondary_button.Enable(enabled)
        self._reset_button.Enable(self._has_overrides())

    def _refresh_list(self, select_index=None):
        self._list.DeleteAllItems()
        shortcuts = self._build_primary_map()
        secondary_shortcuts = self._build_secondary_map()
        for index, (action_id, action) in enumerate(self._actions):
            shortcut = shortcuts.get(action_id)
            self._list.InsertItem(index, action.label)
            self._list.SetItem(index, 1, shortcut_to_display(shortcut))
            if self._has_secondary_actions:
                secondary = secondary_shortcuts.get(action_id)
                self._list.SetItem(index, 2, shortcut_to_display(secondary))
        if select_index is not None and 0 <= select_index < self._list.GetItemCount():
            self._list.Select(select_index)
            self._list.Focus(select_index)
            self._list.SetFocus()
        self._update_buttons()

    def _build_primary_map(self):
        shortcuts = {action_id: action.shortcut for action_id, action in self._actions}
        for action_id, shortcut in self._overrides.items():
            shortcuts[action_id] = shortcut
        return shortcuts

    def _build_secondary_map(self):
        shortcuts = {
            action_id: action.shortcut_secondary
            for action_id, action in self._actions
            if action.shortcut_secondary is not None
        }
        for action_id, shortcut in self._secondary_overrides.items():
            shortcuts[action_id] = shortcut
        return shortcuts

    def _on_edit_primary(self, _event):
        index = self._list.GetFirstSelected()
        if index == -1:
            return
        action_id, _action = self._actions[index]
        dialog = self._open_capture_dialog()
        if dialog.ShowModal() == wx.ID_OK:
            new_shortcut = dialog.shortcut
            if new_shortcut and self._has_conflict(action_id, "primary", new_shortcut):
                wx.MessageBox(
                    _("That shortcut is already assigned to another action."),
                    _("Shortcut Conflict"),
                    wx.OK | wx.ICON_ERROR,
                    parent=self,
                )
                dialog.Destroy()
                return
            if new_shortcut:
                self._overrides[action_id] = new_shortcut
                self._refresh_list(select_index=index)
        dialog.Destroy()

    def _on_edit_secondary(self, _event):
        index = self._list.GetFirstSelected()
        if index == -1:
            return
        action_id, action = self._actions[index]
        if not self._supports_secondary(action):
            return
        dialog = self._open_capture_dialog()
        if dialog.ShowModal() == wx.ID_OK:
            new_shortcut = dialog.shortcut
            if new_shortcut and self._has_conflict(action_id, "secondary", new_shortcut):
                wx.MessageBox(
                    _("That shortcut is already assigned to another action."),
                    _("Shortcut Conflict"),
                    wx.OK | wx.ICON_ERROR,
                    parent=self,
                )
                dialog.Destroy()
                return
            if new_shortcut:
                self._secondary_overrides[action_id] = new_shortcut
                self._refresh_list(select_index=index)
        dialog.Destroy()

    def _open_capture_dialog(self):
        if self._capture_mode == "pynput":
            return GlobalShortcutCaptureDialog(self)
        return ShortcutCaptureDialog(self)

    def _has_conflict(self, action_id, slot, new_shortcut):
        for other_id, other_slot, shortcut in self._iter_shortcuts():
            if other_id == action_id and other_slot == slot:
                continue
            if shortcuts_equal(shortcut, new_shortcut):
                return True
        return False

    def _iter_shortcuts(self):
        primary = self._build_primary_map()
        secondary = self._build_secondary_map()
        for other_id, _action in self._actions:
            yield other_id, "primary", primary.get(other_id)
            yield other_id, "secondary", secondary.get(other_id)

    def _supports_secondary(self, action):
        return action.shortcut_secondary is not None

    def _has_overrides(self):
        return bool(self._overrides or self._secondary_overrides)

    def _on_reset(self, _event):
        if not self._has_overrides():
            return
        confirm = wx.MessageBox(
            _("Reset all shortcuts to defaults?"),
            _("Confirm Reset"),
            wx.YES_NO | wx.ICON_QUESTION,
            parent=self,
        )
        if confirm != wx.YES:
            return
        self._overrides.clear()
        self._secondary_overrides.clear()
        self._refresh_list()

