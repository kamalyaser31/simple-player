import os
import tempfile


def atomic_write(path, writer, validator=None, encoding="utf-8"):
    raw_target = str(path or "").strip()
    if not raw_target:
        raise ValueError("Invalid atomic write target path.")
    target = os.path.abspath(raw_target)
    directory = os.path.dirname(target)
    os.makedirs(directory, exist_ok=True)
    descriptor, temporary_path = tempfile.mkstemp(
        prefix=f".{os.path.basename(target)}.", suffix=".tmp", dir=directory
    )
    try:
        handle = os.fdopen(descriptor, "w", encoding=encoding, newline="")
        descriptor = None
        with handle:
            writer(handle)
            handle.flush()
            os.fsync(handle.fileno())
        if validator is not None:
            validator(temporary_path)
        os.replace(temporary_path, target)
    except Exception:
        try:
            if descriptor is not None:
                os.close(descriptor)
        except OSError:
            pass
        try:
            os.remove(temporary_path)
        except FileNotFoundError:
            pass
        raise
