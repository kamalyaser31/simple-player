import os
import sys
import winreg
import ctypes

from config.constants import APP_NAME, AUDIO_EXTENSIONS


APP_PROGID = "SimpleAudioPlayer.media"
APP_REG_NAME = "Simple Audio Player"
LEGACY_APP_EXE_ALIAS = "main.exe"
CAPABILITIES_KEY = r"Software\SimpleAudioPlayer\Capabilities"
REGISTERED_APPS_KEY = r"Software\RegisteredApplications"
CLASSES_ROOT = r"Software\Classes"
CONTEXT_MENU_LABEL = "Play with Simple Audio Player"
VIDEO_EXTENSIONS = {
    ".3gp",
    ".avi",
    ".flv",
    ".m2ts",
    ".m4v",
    ".mkv",
    ".mov",
    ".mpeg",
    ".mp4",
    ".mpg",
    ".ts",
    ".webm",
    ".wmv",
}


def register_file_associations():
    command = _build_open_command()
    exe_alias = _build_exe_alias()
    extensions = _association_extensions()
    try:
        _write_progid(command)
        _write_application_registration(command, exe_alias, extensions)
        _write_extension_associations(extensions)
        _notify_association_change()
        return True, ""
    except OSError as exc:
        return False, str(exc)


def unregister_file_associations():
    exe_alias = _build_exe_alias()
    extensions = _association_extensions()
    try:
        _remove_extension_associations(extensions)
        _delete_tree(winreg.HKEY_CURRENT_USER, fr"{CLASSES_ROOT}\{APP_PROGID}")
        _delete_tree(winreg.HKEY_CURRENT_USER, fr"{CLASSES_ROOT}\Applications\{exe_alias}")
        _delete_tree(winreg.HKEY_CURRENT_USER, fr"{CLASSES_ROOT}\Applications\{LEGACY_APP_EXE_ALIAS}")
        _delete_tree(winreg.HKEY_CURRENT_USER, CAPABILITIES_KEY)
        _delete_value(winreg.HKEY_CURRENT_USER, REGISTERED_APPS_KEY, APP_REG_NAME)
        _notify_association_change()
        return True, ""
    except OSError as exc:
        return False, str(exc)


def _write_progid(command):
    progid_key = fr"{CLASSES_ROOT}\{APP_PROGID}"
    _set_default_value(winreg.HKEY_CURRENT_USER, progid_key, f"{APP_NAME} media file")
    _set_default_value(
        winreg.HKEY_CURRENT_USER,
        fr"{progid_key}\shell\open\command",
        command,
    )
    _set_default_value(
        winreg.HKEY_CURRENT_USER,
        fr"{progid_key}\shell\play_with_simple_audio_player",
        CONTEXT_MENU_LABEL,
    )
    _set_default_value(
        winreg.HKEY_CURRENT_USER,
        fr"{progid_key}\shell\play_with_simple_audio_player\command",
        command,
    )


def _write_application_registration(command, exe_alias, extensions):
    app_key = fr"{CLASSES_ROOT}\Applications\{exe_alias}"
    _set_string_value(winreg.HKEY_CURRENT_USER, app_key, "FriendlyAppName", APP_NAME)
    _set_default_value(
        winreg.HKEY_CURRENT_USER,
        fr"{app_key}\shell\open\command",
        command,
    )
    _set_default_value(
        winreg.HKEY_CURRENT_USER,
        fr"{app_key}\shell\play_with_simple_audio_player",
        CONTEXT_MENU_LABEL,
    )
    _set_default_value(
        winreg.HKEY_CURRENT_USER,
        fr"{app_key}\shell\play_with_simple_audio_player\command",
        command,
    )
    for ext in extensions:
        _set_string_value(
            winreg.HKEY_CURRENT_USER,
            fr"{app_key}\SupportedTypes",
            ext,
            "",
        )

    _set_string_value(
        winreg.HKEY_CURRENT_USER,
        CAPABILITIES_KEY,
        "ApplicationName",
        APP_NAME,
    )
    _set_string_value(
        winreg.HKEY_CURRENT_USER,
        CAPABILITIES_KEY,
        "ApplicationDescription",
        "Play audio and media files with Simple Audio Player.",
    )
    for ext in extensions:
        _set_string_value(
            winreg.HKEY_CURRENT_USER,
            fr"{CAPABILITIES_KEY}\FileAssociations",
            ext,
            APP_PROGID,
        )
    _set_string_value(
        winreg.HKEY_CURRENT_USER,
        REGISTERED_APPS_KEY,
        APP_REG_NAME,
        CAPABILITIES_KEY,
    )


def _write_extension_associations(extensions):
    for ext in extensions:
        ext_key = fr"{CLASSES_ROOT}\{ext}"
        _set_default_value(winreg.HKEY_CURRENT_USER, ext_key, APP_PROGID)
        _set_binary_value(
            winreg.HKEY_CURRENT_USER,
            fr"{ext_key}\OpenWithProgids",
            APP_PROGID,
            b"",
        )


def _remove_extension_associations(extensions):
    for ext in extensions:
        ext_key = fr"{CLASSES_ROOT}\{ext}"
        current_default = _get_default_value(winreg.HKEY_CURRENT_USER, ext_key)
        if current_default == APP_PROGID:
            _set_default_value(winreg.HKEY_CURRENT_USER, ext_key, "")
        _delete_value(
            winreg.HKEY_CURRENT_USER,
            fr"{ext_key}\OpenWithProgids",
            APP_PROGID,
        )


def _build_open_command():
    exe_path = _build_exe_path()
    if getattr(sys, "frozen", False):
        return f'"{exe_path}" "%1"'
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    script_path = os.path.join(root, "SimpleAudioPlayer.py")
    if not os.path.isfile(script_path):
        script_path = os.path.join(root, "main.py")
    return f'"{exe_path}" "{script_path}" "%1"'


def _build_exe_path():
    exe_path = sys.executable
    if exe_path.lower().endswith("python.exe"):
        pythonw_path = os.path.join(os.path.dirname(exe_path), "pythonw.exe")
        if os.path.isfile(pythonw_path):
            exe_path = pythonw_path
    return exe_path


def _build_exe_alias():
    return os.path.basename(_build_exe_path())


def _association_extensions():
    return sorted(set(AUDIO_EXTENSIONS) | VIDEO_EXTENSIONS)


def _set_default_value(root, path, value):
    with winreg.CreateKeyEx(root, path, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, value)


def _set_string_value(root, path, name, value):
    with winreg.CreateKeyEx(root, path, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)


def _set_binary_value(root, path, name, value):
    with winreg.CreateKeyEx(root, path, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_BINARY, value)


def _get_default_value(root, path):
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
            value, _value_type = winreg.QueryValueEx(key, "")
            return value
    except OSError:
        return ""


def _delete_value(root, path, name):
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
    except OSError:
        pass


def _delete_tree(root, path):
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            while True:
                child = winreg.EnumKey(key, 0)
                _delete_tree(root, f"{path}\\{child}")
    except OSError:
        pass
    try:
        winreg.DeleteKey(root, path)
    except OSError:
        pass


def _notify_association_change():
    try:
        shell32 = ctypes.windll.shell32
        shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
    except Exception:
        pass

