import json
import os
import tempfile


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
    base = os.path.dirname(target)
    if base:
        os.makedirs(base, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(prefix="sap_favs_", suffix=".tmp", dir=base or None)
    os.close(fd)
    try:
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        os.replace(tmp_path, target)
    except Exception:
        try:
            if os.path.isfile(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass
        raise
