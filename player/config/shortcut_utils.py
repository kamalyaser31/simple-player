from gettext import gettext as _

import wx

from config.shortcuts import Shortcut


MODIFIER_ORDER = ["ctrl", "shift", "alt", "win"]
_MODIFIER_ALIASES = {
    "ctrl": "ctrl",
    "control": "ctrl",
    "shift": "shift",
    "alt": "alt",
    "win": "win",
    "windows": "win",
    "meta": "win",
    "super": "win",
}

_KEY_ALIASES = {
    "pageup": "page_up",
    "pgup": "page_up",
    "pagedown": "page_down",
    "pgdn": "page_down",
    "del": "delete",
}

_KEY_DISPLAY = {
    "space": _("Space"),
    "tab": _("Tab"),
    "enter": _("Enter"),
    "backspace": _("Backspace"),
    "left": _("Left"),
    "right": _("Right"),
    "up": _("Up"),
    "down": _("Down"),
    "page_up": _("Page Up"),
    "page_down": _("Page Down"),
    "home": _("Home"),
    "end": _("End"),
    "delete": _("Delete"),
}


def shortcut_to_display(shortcut):
    if shortcut is None:
        return ""
    parts = []
    for modifier in MODIFIER_ORDER:
        if modifier in shortcut.modifiers:
            parts.append(modifier.title())
    key = _display_key(shortcut.key)
    if key:
        parts.append(key)
    return "+".join(parts)


def shortcut_to_config(shortcut):
    if shortcut is None:
        return ""
    parts = []
    for modifier in MODIFIER_ORDER:
        if modifier in shortcut.modifiers:
            parts.append(modifier)
    parts.append(shortcut.key)
    return "+".join(parts)


def shortcut_from_config(text):
    if not text:
        return None
    tokens = [token.strip().lower() for token in text.split("+") if token.strip()]
    if not tokens:
        return None
    modifiers = set()
    key = None
    for token in tokens:
        canonical_modifier = _MODIFIER_ALIASES.get(token)
        if canonical_modifier:
            modifiers.add(canonical_modifier)
            continue
        if key is not None:
            return None
        key = _canonical_key(token)
    if not key:
        return None
    return Shortcut(key, frozenset(modifiers))


def shortcut_from_event(event):
    key = _key_from_event(event)
    if not key:
        return None
    modifiers = _modifiers_from_event(event)
    return Shortcut(key, frozenset(modifiers))


def shortcuts_equal(left, right):
    if left is None and right is None:
        return True
    if left is None or right is None:
        return False
    return left.key == right.key and left.modifiers == right.modifiers


def _canonical_key(token):
    if token == "_":
        token = "-"
    token = _KEY_ALIASES.get(token, token)
    if token.startswith("f") and token[1:].isdigit():
        return token
    if len(token) == 1:
        return token
    return token


def _display_key(key):
    if key in _KEY_DISPLAY:
        return _KEY_DISPLAY[key]
    if key.startswith("f") and key[1:].isdigit():
        return key.upper()
    if len(key) == 1:
        return key.upper()
    return key.title()


def _key_from_event(event):
    keycode = event.GetKeyCode()
    if keycode in (
        wx.WXK_SHIFT,
        wx.WXK_CONTROL,
        wx.WXK_ALT,
        wx.WXK_WINDOWS_LEFT,
        wx.WXK_WINDOWS_RIGHT,
    ):
        return ""
    if wx.WXK_F1 <= keycode <= wx.WXK_F24:
        return f"f{keycode - wx.WXK_F1 + 1}"
    key_map = {
        wx.WXK_SPACE: "space",
        wx.WXK_TAB: "tab",
        wx.WXK_RETURN: "enter",
        wx.WXK_NUMPAD_ENTER: "enter",
        wx.WXK_BACK: "backspace",
        wx.WXK_DELETE: "delete",
        wx.WXK_HOME: "home",
        wx.WXK_END: "end",
        wx.WXK_PAGEUP: "page_up",
        wx.WXK_PAGEDOWN: "page_down",
        wx.WXK_LEFT: "left",
        wx.WXK_RIGHT: "right",
        wx.WXK_UP: "up",
        wx.WXK_DOWN: "down",
    }
    if keycode in key_map:
        return key_map[keycode]
    if 48 <= keycode <= 57:
        return chr(keycode)
    if 65 <= keycode <= 90:
        return chr(keycode).lower()
    unicode_key = event.GetUnicodeKey()
    if unicode_key != wx.WXK_NONE and unicode_key >= 32:
        char = chr(unicode_key).lower()
        if char == "_" and event.ShiftDown():
            return "-"
        return char
    if 32 <= keycode <= 126:
        return chr(keycode).lower()
    return ""


def _modifiers_from_event(event):
    modifiers = set()
    mask = event.GetModifiers()

    control_mask = (
        wx.MOD_CONTROL
        | getattr(wx, "MOD_RAW_CONTROL", 0)
        | getattr(wx, "MOD_CMD", 0)
    )
    if (mask & control_mask) or event.ControlDown():
        modifiers.add("ctrl")
    if (mask & wx.MOD_SHIFT) or event.ShiftDown():
        modifiers.add("shift")
    if (mask & wx.MOD_ALT) or event.AltDown():
        modifiers.add("alt")

    win_mask = getattr(wx, "MOD_WIN", 0) | getattr(wx, "MOD_META", 0)
    if (mask & win_mask) or event.MetaDown():
        modifiers.add("win")

    return modifiers

