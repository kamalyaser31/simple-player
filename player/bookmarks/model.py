from dataclasses import dataclass


@dataclass
class Mark:
    id: str
    name: str
    path: str
    pos: float
    created: float


def mark_from_dict(data, fallback_path=""):
    if not isinstance(data, dict):
        return None
    mark_id = str(data.get("id") or "").strip()
    name = str(data.get("name") or "").strip()
    path = str(data.get("path") or fallback_path or "").strip()
    if not mark_id or not name or not path:
        return None
    try:
        pos = float(data.get("pos", 0.0) or 0.0)
    except (TypeError, ValueError):
        pos = 0.0
    if pos < 0:
        pos = 0.0
    try:
        created = float(data.get("created", 0.0) or 0.0)
    except (TypeError, ValueError):
        created = 0.0
    return Mark(
        id=mark_id,
        name=name,
        path=path,
        pos=pos,
        created=created,
    )


def mark_to_dict(mark):
    return {
        "id": str(mark.id or "").strip(),
        "name": str(mark.name or "").strip(),
        "path": str(mark.path or "").strip(),
        "pos": float(mark.pos or 0.0),
        "created": float(mark.created or 0.0),
    }
