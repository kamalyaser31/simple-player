from dataclasses import dataclass


FAV_TYPES = (
    "video",
    "playlist",
    "combined",
    "generic_stream",
)


@dataclass
class Fav:
    id: str
    name: str
    kind: str
    link: str
    created: float


def fav_from_dict(data):
    if not isinstance(data, dict):
        return None
    fav_id = str(data.get("id") or "").strip()
    name = str(data.get("name") or "").strip()
    kind = str(data.get("kind") or "").strip().lower()
    link = str(data.get("link") or "").strip()
    if not fav_id or not name or not link:
        return None
    if kind not in FAV_TYPES:
        return None
    try:
        created = float(data.get("created", 0.0) or 0.0)
    except (TypeError, ValueError):
        created = 0.0
    return Fav(
        id=fav_id,
        name=name,
        kind=kind,
        link=link,
        created=created,
    )


def fav_to_dict(item):
    return {
        "id": str(item.id or "").strip(),
        "name": str(item.name or "").strip(),
        "kind": str(item.kind or "").strip().lower(),
        "link": str(item.link or "").strip(),
        "created": float(item.created or 0.0),
    }
