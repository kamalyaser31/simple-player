import os
from urllib.parse import unquote, urlparse

import wx


def set_clipboard_files(paths):
    valid_paths = [path for path in (paths or []) if path and os.path.exists(path)]
    if not valid_paths:
        return False

    data = wx.FileDataObject()
    for path in valid_paths:
        data.AddFile(path)
    if not data.GetFilenames():
        return False

    clipboard = wx.Clipboard.Get()
    if not clipboard.Open():
        return False
    try:
        if not clipboard.SetData(data):
            return False
        clipboard.Flush()
        return True
    finally:
        clipboard.Close()


def get_clipboard_paths():
    clipboard = wx.Clipboard.Get()
    if not clipboard.Open():
        return []
    try:
        file_data = wx.FileDataObject()
        if clipboard.GetData(file_data):
            paths = [path for path in file_data.GetFilenames() if path]
            if paths:
                return paths

        text_data = wx.TextDataObject()
        if clipboard.GetData(text_data):
            text = text_data.GetText() or ""
            return _extract_paths_from_text(text)
    finally:
        clipboard.Close()
    return []


def _extract_paths_from_text(text):
    if not text:
        return []
    items = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith('"') and line.endswith('"') and len(line) >= 2:
            line = line[1:-1]
        path = _parse_file_uri_or_path(line)
        if path:
            items.append(path)
    return items


def _parse_file_uri_or_path(value):
    text = str(value or "").strip()
    parsed = urlparse(text)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        low = text.lower()
        if low.startswith("http://") or low.startswith("https://"):
            return text
    lowered = value.lower()
    if lowered.startswith("file://"):
        parsed = urlparse(value)
        if parsed.scheme != "file":
            return ""
        candidate = unquote(parsed.path or "")
        if candidate.startswith("/") and len(candidate) >= 3 and candidate[2] == ":":
            candidate = candidate[1:]
        return os.path.normpath(candidate)
    return os.path.normpath(value)
