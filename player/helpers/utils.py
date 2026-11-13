import math
from gettext import gettext as _


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def format_time(seconds):
    if seconds is None:
        return None
    try:
        seconds = float(seconds)
    except (TypeError, ValueError):
        return None
    if math.isnan(seconds) or math.isinf(seconds):
        return None
    if seconds < 0:
        seconds = 0
    total = int(round(seconds))
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def fmt_bytes(value):
    try:
        num = int(value)
    except Exception:
        num = 0
    if num <= 0:
        return _("Unknown")
    size = float(num)
    units = ("B", "KB", "MB", "GB", "TB")
    idx = 0
    while size >= 1024.0 and idx < len(units) - 1:
        size /= 1024.0
        idx += 1
    if idx == 0:
        return f"{int(size)} {units[idx]}"
    return f"{size:.2f} {units[idx]}"
