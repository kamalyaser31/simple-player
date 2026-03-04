from dataclasses import dataclass


@dataclass
class Pos:
    path: str
    pos: float
    updated: float


def pos_from_dict(data, fallback_path=""):
    if not isinstance(data, dict):
        return None
    path = str(data.get("path") or fallback_path or "").strip()
    if not path:
        return None
    try:
        pos = float(data.get("pos", 0.0) or 0.0)
    except (TypeError, ValueError):
        pos = 0.0
    if pos < 0:
        pos = 0.0
    try:
        updated = float(data.get("updated", 0.0) or 0.0)
    except (TypeError, ValueError):
        updated = 0.0
    return Pos(
        path=path,
        pos=pos,
        updated=updated,
    )


def pos_to_dict(item):
    return {
        "path": str(item.path or "").strip(),
        "pos": float(item.pos or 0.0),
        "updated": float(item.updated or 0.0),
    }
