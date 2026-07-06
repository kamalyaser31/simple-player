import os

from config.constants import AUDIO_EXTENSIONS


def collect_audio_files(folder_path, recursive=False):
    entries = []
    try:
        if recursive:
            for root, _dirs, files in os.walk(folder_path):
                for name in files:
                    _, ext = os.path.splitext(name)
                    if ext.lower() in AUDIO_EXTENSIONS:
                        entries.append(os.path.join(root, name))
        else:
            for name in os.listdir(folder_path):
                full = os.path.join(folder_path, name)
                if not os.path.isfile(full):
                    continue
                _, ext = os.path.splitext(name)
                if ext.lower() in AUDIO_EXTENSIONS:
                    entries.append(full)
    except OSError:
        return []

    if recursive:
        entries.sort(key=lambda p: p.lower())
    else:
        entries.sort(key=lambda p: os.path.basename(p).lower())
    return entries


def collect_audio_files_with_progress(folder_path, on_progress=None, should_cancel=None):
    def is_cancelled():
        if should_cancel is None:
            return False
        try:
            return bool(should_cancel())
        except Exception:
            return False

    def emit(data):
        if on_progress is None:
            return
        try:
            on_progress(dict(data))
        except Exception:
            pass

    total_files = 0
    counted = 0
    try:
        for _root, _dirs, files in os.walk(folder_path):
            if is_cancelled():
                return None
            count = len(files)
            total_files += count
            counted += count
            if counted % 500 == 0:
                emit(
                    {
                        "phase": "count",
                        "counted": counted,
                        "total": 0,
                        "processed": 0,
                        "found": 0,
                        "pct": 0.0,
                    }
                )
    except OSError:
        return []

    emit(
        {
            "phase": "count",
            "counted": counted,
            "total": total_files,
            "processed": 0,
            "found": 0,
            "pct": 0.0,
        }
    )
    if total_files <= 0:
        return []

    entries = []
    processed = 0
    try:
        for root, _dirs, files in os.walk(folder_path):
            if is_cancelled():
                return None
            for name in files:
                if is_cancelled():
                    return None
                processed += 1
                _, ext = os.path.splitext(name)
                if ext.lower() in AUDIO_EXTENSIONS:
                    entries.append(os.path.join(root, name))
                if processed == total_files or processed % 200 == 0:
                    pct = (processed / total_files) * 100.0
                    emit(
                        {
                            "phase": "collect",
                            "counted": total_files,
                            "total": total_files,
                            "processed": processed,
                            "found": len(entries),
                            "pct": pct,
                        }
                    )
    except OSError:
        return []

    entries.sort(key=lambda p: p.lower())
    emit(
        {
            "phase": "collect",
            "counted": total_files,
            "total": total_files,
            "processed": total_files,
            "found": len(entries),
            "pct": 100.0,
        }
    )
    return entries

