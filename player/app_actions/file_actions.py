import concurrent.futures
import os
import queue
import time
import ctypes
from ctypes import wintypes

from gettext import gettext as _

import wx

from config.localization import app_root
from core.media_library import collect_audio_files, collect_audio_files_with_progress
from helpers.clipboard_utils import get_clipboard_paths, set_clipboard_files
from helpers.file_helpers import (
    is_http_url,
    res_clip,
    res_shell,
    set_empty,
    set_ready,
    set_switched,
    show_name,
)
from ui import dialogs
from youtube.actions import open_yt_link, sync_sel, try_next
from youtube.link_validator import parse_link
from youtube.state import clear_ses
from ui.task_dialogs import BusyDialog


def _open_with_mode(ctx, path, start_position=None):
    mode = ctx.settings.get_open_with_files_mode()
    if mode == "main_folder":
        ok = ctx.player.open_file_with_folder(
            path,
            recursive=False,
            start_position=start_position,
        )
    elif mode == "main_and_subfolders":
        ok = _open_with_subfolders_loading(ctx, path, start_position=start_position)
    else:
        ok = ctx.player.open_file(path, start_position=start_position)
    if ok:
        set_ready(ctx)
    return bool(ok)


def _open_with_subfolders_loading(ctx, path, start_position=None):
    folder_path = os.path.dirname(path)
    if not folder_path:
        return False

    if ctx.frame is None:
        files = collect_audio_files(folder_path, recursive=True)
        if not files:
            return False
        return bool(
            ctx.player.open_file_list(
                files,
                preferred_path=path,
                start_position=start_position,
            )
        )

    dlg = BusyDialog(ctx.frame, _("Opening files"), _("Loading files from folder and subfolders..."))
    updates = queue.Queue()
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = pool.submit(
        collect_audio_files_with_progress,
        folder_path,
        on_progress=updates.put,
        should_cancel=lambda: bool(state["cancelled"]),
    )
    timer = wx.Timer(dlg)
    state = {"finished": False, "cancelled": False, "determinate": False}

    def on_tick(_event):
        if dlg.was_cancelled():
            state["cancelled"] = True

        while True:
            try:
                payload = updates.get_nowait()
            except queue.Empty:
                break
            label, pct = _fmt_recursive_open_progress(payload)
            if label:
                dlg.set_label(label)
            if pct is None:
                if not state["determinate"]:
                    dlg.pulse()
            else:
                state["determinate"] = True
                dlg.set_progress(pct)

        if state["cancelled"] and not state["finished"]:
            state["finished"] = True
            dlg.EndModal(wx.ID_CANCEL)
            return

        if not future.done() and not state["determinate"]:
            dlg.pulse()

        if future.done() and not state["finished"]:
            state["finished"] = True
            dlg.EndModal(wx.ID_OK)

    dlg.Bind(wx.EVT_TIMER, on_tick, timer)
    timer.Start(60)
    dlg.ShowModal()
    timer.Stop()
    dlg.Destroy()

    if state["cancelled"]:
        pool.shutdown(wait=False, cancel_futures=True)
        return False
    if not future.done():
        pool.shutdown(wait=False, cancel_futures=True)
        return False
    try:
        files = list(future.result() or [])
    except Exception:
        pool.shutdown(wait=False, cancel_futures=True)
        return False
    pool.shutdown(wait=False, cancel_futures=True)
    if not files:
        return False
    return bool(
        ctx.player.open_file_list(
            files,
            preferred_path=path,
            start_position=start_position,
        )
    )


def _fmt_recursive_open_progress(data):
    payload = data if isinstance(data, dict) else {}
    phase = str(payload.get("phase") or "").strip().lower()
    if phase == "count":
        counted = int(payload.get("counted") or 0)
        text = _("Counting files... {count}").format(count=counted)
        return text, None

    total = int(payload.get("total") or 0)
    processed = int(payload.get("processed") or 0)
    found = int(payload.get("found") or 0)
    pct = float(payload.get("pct") or 0.0)
    pct = max(0.0, min(100.0, pct))
    if total > 0:
        text = _(
            "Opening files... {found} media files found ({done}/{total}) - {pct:.1f}%"
        ).format(
            found=found,
            done=processed,
            total=total,
            pct=pct,
        )
    else:
        text = _("Opening files... {found} media files found").format(found=found)
    return text, pct


def open_paths(ctx, raw_paths):
    paths = []
    for raw in raw_paths or []:
        path = res_shell(raw)
        if path:
            paths.append(path)
    if not paths:
        return False

    first = paths[0]
    if os.path.isdir(first):
        clear_ses(ctx)
        ok = ctx.player.open_folder(first)
        if ok:
            ctx.settings.set_last_dir(first)
            set_ready(ctx)
        return bool(ok)

    if os.path.isfile(first):
        files = [path for path in paths if os.path.isfile(path)]
        if not files:
            files = [first]
        if _open_shell_files(ctx, files):
            return True
    return False


def _open_shell_files(ctx, files):
    entries = [path for path in files if path]
    if not entries:
        return False

    first = entries[0]
    mode = ctx.settings.get_open_with_files_mode()

    clear_ses(ctx)
    ok = False
    if mode == "file_only" and len(entries) > 1:
        ok = bool(
            ctx.player.open_file_list(
                entries,
                preferred_path=first,
                start_position=None,
            )
        )
        if ok:
            set_ready(ctx)
    else:
        ok = bool(_open_with_mode(ctx, first))

    if ok:
        ctx.settings.set_last_dir(os.path.dirname(first))
        return True
    return False


def open_file(ctx):
    if ctx.frame is None:
        return
    path, folder = dialogs.open_file_dialog(ctx.frame, ctx.settings.get_last_dir())
    if not path:
        return
    ctx.settings.set_last_dir(folder or os.path.dirname(path))
    clear_ses(ctx)
    _open_with_mode(ctx, path)


def open_folder(ctx):
    if ctx.frame is None:
        return
    folder = dialogs.open_folder_dialog(ctx.frame, ctx.settings.get_last_dir())
    if not folder:
        return
    ctx.settings.set_last_dir(folder)
    clear_ses(ctx)
    ok = ctx.player.open_folder(folder)
    if not ok:
        ctx.speak(_("No audio files found in that folder."), _("No audio files."))
        return
    set_ready(ctx)


def open_link(ctx):
    if ctx.frame is None:
        return
    dlg = wx.TextEntryDialog(ctx.frame, _("Enter link to play."), _("Open Link"))
    if dlg.ShowModal() == wx.ID_OK:
        url = dlg.GetValue().strip()
        if not is_http_url(url):
            wx.MessageBox(
                _("The link must start with http or https."),
                _("Invalid link"),
                wx.OK | wx.ICON_ERROR,
                parent=ctx.frame,
            )
        elif ctx.player.open_stream(url, append=True):
            clear_ses(ctx)
            set_ready(ctx)
        else:
            wx.MessageBox(
                _("Could not open the link."),
                _("Error"),
                wx.OK | wx.ICON_ERROR,
                parent=ctx.frame,
            )
    dlg.Destroy()


def open_here(ctx):
    path = ctx.player.current_path
    if not path:
        ctx.speak(_("No file loaded."), _("No file."))
        return
    folder = os.path.dirname(path)
    if not folder:
        ctx.speak(_("No file loaded."), _("No file."))
        return
    try:
        os.startfile(folder)
    except OSError:
        ctx.speak(_("Could not open the folder."), _("Open failed."))


def open_props(ctx):
    path = ctx.player.current_path
    if not path:
        ctx.speak(_("No file loaded."), _("No file."))
        return
    if not os.path.isfile(path):
        ctx.speak(
            _("File properties are available only for local files."),
            _("Not available for streams."),
        )
        return
    if os.name != "nt":
        ctx.speak(_("File properties are not supported on this platform."), _("Not supported."))
        return
    target = os.path.normpath(os.path.abspath(path))
    ok, err = _show_props_win(target)
    if not ok:
        if err:
            ctx.speak(
                _("Could not open file properties."),
                _("Could not open file properties: {error}").format(error=err),
            )
        else:
            ctx.speak(_("Could not open file properties."), _("Open failed."))


def _show_props_win(path):
    # Preferred API for showing the standard Explorer properties sheet.
    try:
        fn = ctypes.windll.shell32.SHObjectProperties
        fn.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
        ]
        fn.restype = wintypes.BOOL
        if bool(fn(None, 0x2, path, None)):  # SHOP_FILEPATH
            return True, ""
    except Exception as exc:
        # Continue to ShellExecute fallback.
        err = str(exc)
    else:
        err = ""

    try:
        result = int(
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "properties",
                path,
                None,
                None,
                1,
            )
        )
    except Exception as exc:
        return False, str(exc)
    if result > 32:
        return True, ""
    msg = _shell_error(result)
    if err:
        msg = f"{msg}; {err}" if msg else err
    return False, msg


def _shell_error(code):
    table = {
        0: "Out of memory",
        2: "File not found",
        3: "Path not found",
        5: "Access denied",
        8: "Out of memory",
        26: "Sharing violation",
        27: "Association incomplete",
        28: "DDE timeout",
        29: "DDE failure",
        30: "DDE busy",
        31: "No file association",
        32: "DLL not found",
    }
    text = table.get(int(code), "")
    if text:
        return f"{text} (code {int(code)})"
    return f"ShellExecute error code {int(code)}"


def open_list(ctx):
    if ctx.frame is None:
        return
    files = ctx.player.get_file_list()
    if not files:
        ctx.speak(_("No file loaded."), _("No file."))
        return

    names = []
    for path in files:
        title = str(ctx.player.get_title(path) or "").strip()
        if title:
            names.append(title)
        else:
            names.append(show_name(path))
    dlg = dialogs.OpenedFilesDialog(
        ctx.frame,
        names,
        current_index=ctx.player.get_current_index(),
    )
    dlg.info_button.Bind(wx.EVT_BUTTON, lambda _e: _show_playlist_info(dlg, ctx, files))
    if dlg.ShowModal() == wx.ID_OK:
        idx = dlg.get_selection()
        if idx != wx.NOT_FOUND and ctx.player.jump_to_index(idx):
            _restore_pos(ctx)
            set_ready(ctx)
    dlg.Destroy()


def _show_playlist_info(parent, ctx, files):
    try:
        from playlist.info import show as show_pl_info
    except Exception:
        ctx.speak(_("Could not load playlist info."), _("Info failed."))
        return
    show_pl_info(parent, ctx, files)


def spk_test(ctx):
    sound = os.path.join(app_root(), "sounds", "speaker_test.wav")
    if not os.path.isfile(sound):
        ctx.speak(_("Speaker test file not found."), _("Test file missing."))
        return
    if ctx.player.play_test_speakers_sound(sound):
        ctx.speak(_("Testing speakers."), _("Testing speakers."))
    else:
        ctx.speak(_("Unable to play speaker test."), _("Test failed."))


def restore_last(ctx):
    if not ctx.settings.get_remember_position():
        return
    path = ctx.settings.get_last_file()
    if not path or not os.path.isfile(path):
        return
    pos = ctx.settings.get_last_position()
    if _open_with_mode(ctx, path, start_position=pos):
        return


def goto_file(ctx):
    if ctx.frame is None:
        return
    count = ctx.player.get_count()
    if count <= 1:
        ctx.speak(_("No other files are loaded."), _("No other files."))
        return
    dlg = wx.TextEntryDialog(
        ctx.frame,
        _("Enter file number (1-{count})").format(count=count),
        _("Go To File"),
    )
    if dlg.ShowModal() == wx.ID_OK:
        text = dlg.GetValue().strip()
        try:
            idx = int(text) - 1
        except ValueError:
            ctx.speak(_("Invalid file number."), _("Invalid number."))
            dlg.Destroy()
            return
        if idx < 0 or idx >= count:
            ctx.speak(_("File number out of range."), _("Out of range."))
            dlg.Destroy()
            return
        if ctx.player.jump_to_index(idx):
            _restore_pos(ctx)
            set_ready(ctx)
    dlg.Destroy()


def next_file(ctx):
    _save_pos(ctx)
    current = str(ctx.player.current_path or "")
    if current and str(ctx.selection_path or "") == current:
        if ctx.selection_start is not None or ctx.selection_end is not None:
            ctx.reset_selection()
    moved = try_next(ctx)
    if moved is None:
        moved = bool(ctx.player.next_track())
        if moved:
            sync_sel(ctx)
    if moved:
        _restore_pos(ctx)
        set_switched(ctx)
        if ctx.settings.get_speak_file_on_nav():
            filename = show_name(ctx.player.current_path)
            ctx.speak(filename, filename)


def prev_file(ctx):
    _save_pos(ctx)
    if ctx.player.previous_track():
        _restore_pos(ctx)
        sync_sel(ctx)
        set_switched(ctx)
        if ctx.settings.get_speak_file_on_nav():
            filename = show_name(ctx.player.current_path)
            ctx.speak(filename, filename)


def first_file(ctx):
    if ctx.player.go_to_first_file():
        _restore_pos(ctx)
        set_switched(ctx)


def last_file(ctx):
    if ctx.player.go_to_last_file():
        _restore_pos(ctx)
        set_switched(ctx)


def close_file(ctx):
    if not ctx.player.current_path:
        ctx.speak(_("No file loaded."), _("No file."))
        return
    ok, new_path = ctx.player.close_current_file()
    if not ok:
        ctx.speak(_("Could not close the file."), _("Close failed."))
        return
    if new_path is None:
        set_empty(ctx)
    else:
        set_ready(ctx)
    ctx.speak(_("File closed."), _("File closed."))


def close_all_files(ctx):
    if not ctx.player.current_path and ctx.player.get_count() <= 0:
        ctx.speak(_("No file loaded."), _("No file."))
        return
    if not ctx.player.close_all_files():
        ctx.speak(_("Could not close files."), _("Close failed."))
        return
    clear_ses(ctx)
    set_empty(ctx)
    ctx.speak(_("All files closed."), _("All files closed."))


def copy_file(ctx):
    path = ctx.player.current_path
    if not path:
        ctx.speak(_("No file loaded."), _("No file."))
        return
    if set_clipboard_files([path]):
        ctx.speak(_("Current file copied to clipboard."), _("Copied."))
    else:
        ctx.speak(_("Unable to copy current file to clipboard."), _("Copy failed."))


def paste_files(ctx):
    paths = get_clipboard_paths()
    if not paths:
        ctx.speak(_("Clipboard does not contain files or folders."), _("Clipboard empty."))
        return

    bad = []
    for raw in paths:
        url = str(raw or "").strip()
        info = parse_link(url)
        if info.is_http:
            if info.is_youtube:
                open_yt_link(ctx, info.raw)
                return
            clear_ses(ctx)
            if ctx.player.open_stream(info.raw, append=True):
                set_ready(ctx)
                return
            wx.MessageBox(
                _("Could not open the link from clipboard."),
                _("Error"),
                wx.OK | wx.ICON_ERROR,
                parent=ctx.frame,
            )
            return

        path = res_clip(raw)
        if not path:
            bad.append(raw)
            continue

        if os.path.isdir(path):
            clear_ses(ctx)
            ok = ctx.player.open_folder(path)
            if not ok:
                ctx.speak(_("No audio files found in that folder."), _("No audio files."))
                return
            ctx.settings.set_last_dir(path)
            set_ready(ctx)
            return

        if os.path.isfile(path):
            clear_ses(ctx)
            if _open_with_mode(ctx, path):
                ctx.settings.set_last_dir(os.path.dirname(path))
                return
            ctx.speak(_("Could not open the file from clipboard."), _("Open failed."))
            return

        bad.append(raw)

    if bad:
        ctx.speak(
            _("Clipboard path could not be resolved: {path}").format(path=bad[0]),
            _("Invalid path in clipboard."),
        )
    else:
        ctx.speak(_("Clipboard does not contain openable files or folders."), _("Cannot open clipboard data."))


def del_file(ctx):
    path = ctx.player.current_path
    if not path:
        ctx.speak(_("No file loaded."), _("No file."))
        return
    if not os.path.isfile(path):
        ctx.speak(
            _("Delete is available only for local files."),
            _("Not available for streams."),
        )
        return
    name = os.path.basename(path)
    yes = wx.MessageBox(
        _("Delete '{name}'?").format(name=name),
        _("Confirm Delete"),
        wx.YES_NO | wx.ICON_WARNING,
        parent=ctx.frame,
    )
    if yes != wx.YES:
        return
    ok, new_path = ctx.player.delete_current_file()
    if not ok:
        ctx.speak(_("Could not delete the file."), _("Delete failed."))
        return
    if new_path is None:
        set_empty(ctx)
    else:
        set_switched(ctx)
    ctx.speak(_("File deleted."), _("Deleted."))


def ren_file(ctx):
    path = ctx.player.current_path
    if not path:
        ctx.speak(_("No file loaded."), _("No file."))
        return
    if not os.path.isfile(path):
        ctx.speak(
            _("Rename is available only for local files."),
            _("Not available for streams."),
        )
        return
    name = os.path.basename(path)
    dlg = wx.TextEntryDialog(
        ctx.frame,
        _("Enter new name for the file."),
        _("Rename File"),
        value=name,
    )
    if dlg.ShowModal() == wx.ID_OK:
        new_name = os.path.basename(dlg.GetValue().strip())
        ok, _new = ctx.player.rename_current_file(new_name)
        if ok:
            ctx.speak(_("File renamed."), _("Renamed."))
        else:
            ctx.speak(_("Could not rename the file."), _("Rename failed."))
    dlg.Destroy()


def say_file(ctx):
    path = ctx.player.current_path
    if not path:
        ctx.speak(_("No file loaded."), _("No file."))
        return
    title = str(ctx.player.current_title or "").strip()

    now = time.time()
    if ctx.should_reset_file_info():
        ctx.file_info_press_count = 0
    ctx.file_info_last_press = now
    ctx.file_info_press_count += 1

    if ctx.file_info_press_count == 1:
        text = title or os.path.basename(path) or path
        ctx.speak(text, text)
    elif ctx.file_info_press_count == 2:
        ctx.speak(path, path)
    else:
        if _copy_txt(path):
            ctx.speak(_("File path copied to clipboard."), _("Copied."))
        else:
            ctx.speak(_("Unable to copy to clipboard."), _("Copy failed."))
        ctx.file_info_press_count = 0


def _copy_txt(text):
    clip = wx.Clipboard.Get()
    if not clip.Open():
        return False
    try:
        data = wx.TextDataObject()
        data.SetText(text)
        clip.SetData(data)
        clip.Flush()
        return True
    finally:
        clip.Close()


def _save_pos(ctx):
    if not _can_track_pos(ctx):
        return
    path = str(ctx.player.current_path or "").strip()
    if not path or not os.path.isfile(path):
        return
    raw = ctx.player.get_elapsed()
    if raw is None:
        return
    try:
        pos = float(raw)
    except (TypeError, ValueError):
        return
    if pos < 0:
        pos = 0.0
    try:
        ctx.file_pos.set(path, pos)
    except Exception:
        return


def _restore_pos(ctx):
    if not _can_track_pos(ctx):
        return
    path = str(ctx.player.current_path or "").strip()
    if not path or not os.path.isfile(path):
        return
    try:
        target = ctx.file_pos.get(path)
    except Exception:
        return
    if target is None:
        return
    try:
        value = float(target)
    except (TypeError, ValueError):
        return
    if value <= 0:
        return
    duration = ctx.player.get_duration()
    if duration is not None:
        try:
            value = min(float(value), max(0.0, float(duration)))
        except (TypeError, ValueError):
            return
    ctx.player.set_pending_start(value)
    if not ctx.player.reload_current_file():
        ctx.player.seek_absolute(value)


def _can_track_pos(ctx):
    if not bool(ctx.settings.get_save_file_pos()):
        return False
    if getattr(ctx, "file_pos", None) is None:
        return False
    return True
