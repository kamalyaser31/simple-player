import os
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RecOpts:
    channels: int
    bitrate: int
    fmt: str
    folder: str
    rate: int = 44100
    chunk: int = 1024


def build_name(ext):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = str(ext or "wav").strip().lower()
    return f"recording_{stamp}.{suffix}"


def ensure_folder(path):
    folder = str(path or "").strip()
    if not folder:
        raise ValueError("Recording folder is not set.")
    os.makedirs(folder, exist_ok=True)
    return folder
