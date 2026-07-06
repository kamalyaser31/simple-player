import wx
import json
import traceback
from gettext import gettext as _

from app_guard import AppGuard
import speech
from config.constants import APP_NAME
from config.localization import Localization
from config.settings_manager import SettingsManager
from ui.main_frame import MainFrame
from youtube.startup import check_startup

APP_GUARD_HANDLE = "SimpleAudioPlayer.MainInstance"
APP_GUARD_IPC_HANDLE = "SimpleAudioPlayer.OpenPaths"


class _BootstrapController:
    def __init__(self, settings):
        self._shortcuts = None
        try:
            from actions import ACTIONS
            from config.shortcuts import ShortcutManager

            manager = ShortcutManager(ACTIONS)
            for action_id, shortcut in settings.get_shortcut_overrides().items():
                manager.set(action_id, shortcut)
            for action_id, shortcut in settings.get_secondary_shortcut_overrides().items():
                manager.set(action_id, shortcut, slot="secondary")
            self._shortcuts = manager
        except Exception:
            self._shortcuts = None

    def handle_action(self, _action_id):
        return

    def handle_escape(self):
        return False

    def shutdown(self):
        return

    def open_paths_from_shell(self, _raw_paths):
        return False

    def run_startup_tasks(self):
        return True

    def restore_last_session(self):
        return

    def get_shortcuts(self):
        if self._shortcuts is None:
            return {}
        return self._shortcuts.all_shortcuts()

    def get_shortcut_bindings(self):
        if self._shortcuts is None:
            return {}
        return self._shortcuts.all_bindings()


class SimpleAudioPlayerApp(wx.App):
    def __init__(self, redirect=False, initial_paths=None):
        self._initial_paths = list(initial_paths or [])
        self._guard = None
        self._ipc_handle = APP_GUARD_IPC_HANDLE
        self._ipc_msg = None
        self._pending_open_paths = []
        self._shell_open_queue = []
        self._shell_open_timer = None
        self._controller_ready = False
        self.controller = None
        super().__init__(redirect)

    def OnInit(self):
        if not self._init_guard():
            return False

        self.settings = SettingsManager()
        self.settings.load()
        self.controller = _BootstrapController(self.settings)

        self.localization = Localization()
        self.localization.init(self.settings.get_ui_language())

        frame = MainFrame(self.controller, APP_NAME)
        self.SetTopWindow(frame)
        frame.Show()
        self._shell_open_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_shell_open_timer, self._shell_open_timer)
        self._register_guard_message_handler()
        wx.CallAfter(self._initialize_controller_and_startup)
        return True

    def OnExit(self):
        if self._shell_open_timer is not None and self._shell_open_timer.IsRunning():
            self._shell_open_timer.Stop()
        if self._guard is not None and self._ipc_msg is not None:
            try:
                self._guard.unregister_msg(self._ipc_msg)
            except Exception:
                _log_exc("Failed to unregister AppGuard IPC message.")
            self._ipc_msg = None
        try:
            AppGuard.release()
        except Exception:
            _log_exc("Failed to release AppGuard.")
        return 0

    def _register_guard_message_handler(self):
        if self._guard is None or not self._ipc_handle:
            return
        try:
            self._ipc_msg = self._guard.create_ipc_msg(
                self._ipc_handle,
                self._on_guard_message,
            )
            self._guard.register_msg(self._ipc_msg)
        except Exception:
            _log_exc("Failed to register AppGuard message handler.")
            self._ipc_msg = None

    def _on_guard_message(self, message):
        payload = _extract_guard_message_payload(message)
        if not payload:
            return
        paths = _decode_paths_payload(payload)
        if not paths:
            return
        wx.CallAfter(self._handle_external_open_request, paths)

    def _handle_external_open_request(self, paths):
        frame = self.GetTopWindow()
        if frame is not None:
            try:
                frame.Iconize(False)
            except Exception:
                _log_exc("Could not restore main window from tray state.")
            try:
                frame.Raise()
            except Exception:
                _log_exc("Could not raise main window.")
        self._queue_shell_paths(paths)

    def _queue_shell_paths(self, paths):
        pending = []
        for path in paths or []:
            text = str(path or "").strip()
            if text:
                pending.append(text)
        if not pending:
            return
        if not self._controller_ready:
            self._pending_open_paths.extend(pending)
            return

        self._shell_open_queue.extend(pending)
        if self._shell_open_timer is None:
            self._flush_shell_open_queue()
            return
        self._shell_open_timer.Start(120, oneShot=True)

    def _on_shell_open_timer(self, _event):
        self._flush_shell_open_queue()

    def _flush_shell_open_queue(self):
        paths = list(self._shell_open_queue)
        self._shell_open_queue.clear()
        if paths:
            self._open_paths(paths)

    def _open_paths(self, paths):
        if not self._controller_ready:
            for path in paths or []:
                text = str(path or "").strip()
                if text:
                    self._pending_open_paths.append(text)
            return
        self.controller.open_paths_from_shell(paths)

    def _initialize_controller_and_startup(self):
        frame = self.GetTopWindow()
        if frame is None:
            return
        try:
            from core.controller import AppController

            controller = AppController(self.settings)
        except Exception:
            _log_exc("Failed to initialize app controller.")
            wx.MessageBox(
                _("Could not initialize the application."),
                _("Error"),
                wx.OK | wx.ICON_ERROR,
                parent=frame,
            )
            frame.Close()
            return

        self.controller = controller
        frame.set_controller(controller)
        frame.refresh_shortcuts()
        self.controller.attach_frame(frame)
        self._controller_ready = True
        self._run_startup()

    def _run_startup(self):
        if not self._controller_ready:
            return
        frame = self.GetTopWindow()
        if frame is not None:
            check_startup(frame, self.settings)
            if not self.controller.run_startup_tasks():
                return
        pending = list(self._pending_open_paths)
        self._pending_open_paths.clear()
        startup_paths = []
        if self._initial_paths:
            startup_paths.extend(self._initial_paths)
        if pending:
            startup_paths.extend(pending)
        if startup_paths:
            self._open_paths(startup_paths)
        else:
            self.controller.restore_last_session()
        speech.speak(_("Welcome to Simple Audio Player"))

    def _init_guard(self):
        def _quit_cb():
            return None

        try:
            AppGuard.init(APP_GUARD_HANDLE, _quit_cb, quit_immediate=False)
            self._guard = AppGuard()
        except Exception:
            self._guard = None
            return True

        try:
            if AppGuard.is_primary_instance():
                return True
        except Exception:
            return True

        payload = json.dumps({"paths": self._initial_paths})
        if payload:
            try:
                self._guard.send_msg_request(self._ipc_handle, payload)
            except Exception:
                _log_exc("Failed to send paths to primary instance.")
        try:
            self._guard.focus_window(APP_NAME)
        except Exception:
            _log_exc("Failed to focus primary app window.")
        try:
            AppGuard.release()
        except Exception:
            _log_exc("Failed to release AppGuard in secondary instance.")
        return False


def _extract_guard_message_payload(message):
    if message is None:
        return ""
    if isinstance(message, dict):
        for key in ("msg_data", "data", "message", "msg", "payload"):
            if key not in message:
                continue
            value = message.get(key)
            if value is None:
                continue
            if isinstance(value, bytes):
                try:
                    return value.decode("utf-8", errors="replace")
                except Exception:
                    continue
            return str(value)
        return ""
    if isinstance(message, bytes):
        try:
            return message.decode("utf-8", errors="replace")
        except Exception:
            return ""
    if isinstance(message, str):
        return message
    for attr in ("msg_data", "data", "message", "msg"):
        value = getattr(message, attr, None)
        if value is None:
            continue
        if isinstance(value, bytes):
            try:
                return value.decode("utf-8", errors="replace")
            except Exception:
                continue
        return str(value)
    return ""


def _decode_paths_payload(payload):
    text = str(payload or "").strip()
    if not text:
        return []
    try:
        packet = json.loads(text)
    except Exception:
        # Fallback: allow plain path payloads from external/older senders.
        return [text]
    if not isinstance(packet, dict):
        if isinstance(packet, list):
            return [str(item).strip() for item in packet if str(item).strip()]
        raw = str(packet).strip()
        return [raw] if raw else []
    paths = packet.get("paths", [])
    if not isinstance(paths, list):
        return []
    results = []
    for path in paths:
        if path is None:
            continue
        text = str(path).strip()
        if text:
            results.append(text)
    return results


def _log_exc(message):
    print(f"[SimpleAudioPlayer] {message}")
    traceback.print_exc()

