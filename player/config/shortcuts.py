from dataclasses import dataclass
from typing import FrozenSet


@dataclass(frozen=True)
class Shortcut:
    key: str
    modifiers: FrozenSet[str] = frozenset()


class ShortcutManager:
    def __init__(self, action_definitions):
        self._shortcuts = {
            action_id: action.shortcut
            for action_id, action in action_definitions.items()
            if action.shortcut is not None
        }
        self._secondary = {
            action_id: action.shortcut_secondary
            for action_id, action in action_definitions.items()
            if action.shortcut_secondary is not None
        }

    def all_shortcuts(self):
        return dict(self._shortcuts)

    def all_secondary_shortcuts(self):
        return dict(self._secondary)

    def all_bindings(self):
        bindings = {}
        action_ids = set(self._shortcuts.keys()) | set(self._secondary.keys())
        for action_id in action_ids:
            shortcuts = []
            primary = self._shortcuts.get(action_id)
            secondary = self._secondary.get(action_id)
            if primary is not None:
                shortcuts.append(primary)
            if secondary is not None:
                shortcuts.append(secondary)
            if shortcuts:
                bindings[action_id] = shortcuts
        return bindings

    def get(self, action_id):
        return self._shortcuts.get(action_id)

    def get_secondary(self, action_id):
        return self._secondary.get(action_id)

    def set(self, action_id, shortcut, slot="primary"):
        if slot == "secondary":
            if shortcut is None:
                self._secondary.pop(action_id, None)
            else:
                self._secondary[action_id] = shortcut
            return
        if shortcut is None:
            self._shortcuts.pop(action_id, None)
        else:
            self._shortcuts[action_id] = shortcut
