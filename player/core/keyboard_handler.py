from pynput import keyboard

from config.shortcuts import Shortcut


_MODIFIER_MAP = {
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
}


class KeyboardHandler:
    def __init__(self, shortcuts, on_action):
        self._shortcuts = {}
        self._shortcut_index = {}
        self._on_action = on_action
        self._modifiers = set()
        self._pressed_keys = set()
        self._enabled = True
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            suppress=False,
        )
        self.set_shortcuts(shortcuts)

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def set_enabled(self, enabled):
        self._enabled = bool(enabled)
        if not self._enabled:
            self._modifiers.clear()
            self._pressed_keys.clear()

    def set_shortcuts(self, shortcuts):
        self._shortcuts = dict(shortcuts)
        self._shortcut_index = {}
        for action_id, shortcut_value in self._shortcuts.items():
            for shortcut in _iter_shortcuts(shortcut_value):
                key = shortcut.key
                modifiers = frozenset(shortcut.modifiers)
                self._shortcut_index[(key, modifiers)] = action_id

    def _on_press(self, key):
        modifier = _MODIFIER_MAP.get(key)
        if modifier is not None:
            self._modifiers.add(modifier)
            return
        if not self._enabled:
            return
        token = _key_token(key)
        if token is None:
            return
        if token in self._pressed_keys:
            return
        self._pressed_keys.add(token)
        action_id = self._shortcut_index.get((token, frozenset(self._modifiers)))
        if action_id:
            self._on_action(action_id)

    def _on_release(self, key):
        modifier = _MODIFIER_MAP.get(key)
        if modifier is not None:
            self._modifiers.discard(modifier)
            return
        token = _key_token(key)
        if token is None:
            return
        self._pressed_keys.discard(token)


def _key_token(key):
    if key in _SPECIAL_KEYS:
        return _SPECIAL_KEYS[key]
    name = getattr(key, "name", "")
    if name:
        text = str(name).lower()
        if text.startswith("f") and text[1:].isdigit():
            return text
    if isinstance(key, keyboard.KeyCode) and key.char:
        return key.char.lower()
    return None


def _iter_shortcuts(value):
    if isinstance(value, Shortcut):
        return [value]
    if isinstance(value, (list, tuple)):
        return [shortcut for shortcut in value if isinstance(shortcut, Shortcut)]
    return []

