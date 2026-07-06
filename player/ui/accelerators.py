import wx

from config.shortcuts import Shortcut


_KEY_MAP = {
    "space": wx.WXK_SPACE,
    "tab": wx.WXK_TAB,
    "enter": wx.WXK_RETURN,
    "left": wx.WXK_LEFT,
    "right": wx.WXK_RIGHT,
    "up": wx.WXK_UP,
    "down": wx.WXK_DOWN,
    "page_up": wx.WXK_PAGEUP,
    "page_down": wx.WXK_PAGEDOWN,
    "home": wx.WXK_HOME,
    "end": wx.WXK_END,
    "delete": wx.WXK_DELETE,
    "backspace": wx.WXK_BACK,
    "f2": wx.WXK_F2,
}

_MODIFIER_MAP = {
    "ctrl": wx.ACCEL_CTRL,
    "shift": wx.ACCEL_SHIFT,
    "alt": wx.ACCEL_ALT,
}
_SUPPORTED_MODIFIERS = set(_MODIFIER_MAP.keys())


def build_accelerator_table(shortcuts, reserved_ids=None):
    if reserved_ids is None:
        reserved_ids = {}
    entries = []
    action_id_map = {}
    action_ids = {}

    for action_id, shortcut_entry in shortcuts.items():
        shortcut_values = _iter_shortcuts(shortcut_entry)
        if not shortcut_values:
            continue
        wx_id = reserved_ids.get(action_id)
        if wx_id is None:
            wx_id = action_ids.get(action_id)
            if wx_id is None:
                wx_id = wx.NewIdRef()
                action_ids[action_id] = wx_id
                action_id_map[int(wx_id)] = action_id
        for shortcut in shortcut_values:
            if any(modifier not in _SUPPORTED_MODIFIERS for modifier in shortcut.modifiers):
                # wx.AcceleratorEntry does not support all modifier keys (e.g. Win).
                continue
            keycode = _keycode(shortcut.key)
            if keycode is None:
                continue
            entry = wx.AcceleratorEntry()
            entry.Set(_modifiers(shortcut.modifiers), keycode, int(wx_id))
            entries.append(entry)

    return wx.AcceleratorTable(entries), action_id_map


def _iter_shortcuts(value):
    if isinstance(value, Shortcut):
        return [value]
    if isinstance(value, (list, tuple)):
        return [shortcut for shortcut in value if isinstance(shortcut, Shortcut)]
    return []


def _keycode(key):
    if not key:
        return None
    key = key.lower()
    if key in _KEY_MAP:
        return _KEY_MAP[key]
    if key.startswith("f") and key[1:].isdigit():
        number = int(key[1:])
        if 1 <= number <= 24:
            return wx.WXK_F1 + number - 1
    if len(key) == 1:
        return ord(key.upper())
    return None


def _modifiers(modifiers):
    flags = 0
    for modifier in modifiers:
        flags |= _MODIFIER_MAP.get(modifier, 0)
    return flags

