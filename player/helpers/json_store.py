import json
import os

from helpers.atomic_io import atomic_write


def read_json(path):
    target = str(path or "").strip()
    if not target or not os.path.isfile(target):
        return {}
    try:
        with open(target, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return {}
    if isinstance(data, dict):
        return data
    return {}


def write_json(path, data):
    target = str(path or "").strip()
    if not target:
        raise ValueError("Invalid JSON target path.")
    atomic_write(
        target,
        lambda handle: json.dump(data, handle, ensure_ascii=False, indent=2),
        validator=_validate_json,
    )


def _validate_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        parsed = json.load(handle)
    if not isinstance(parsed, dict):
        raise ValueError("JSON store root must be an object.")
