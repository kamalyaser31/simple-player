import math


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
