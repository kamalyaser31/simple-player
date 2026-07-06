import concurrent.futures
import os
import queue
import shutil
import time

from gettext import gettext as _

import wx
from helpers.clipboard_utils import set_clipboard_files


class _CancelFlag:
    def __init__(self):
        self._cancelled = False

    def set(self):
        self._cancelled = True

    def is_set(self):
        return bool(self._cancelled)


def mark_current_file(ctx):
    marked, _path = ctx.player.toggle_mark_current()
    if marked is None:
        ctx.speak(_("No file loaded."), _("No file."))
        return
    if marked:
        ctx.speak(_("File added to marked files."), _("Marked."))
    else:
        ctx.speak(_("File removed from marked files."), _("Unmarked."))


def mark_all_files(ctx):
    if ctx.player.get_count() <= 0:
        ctx.speak(_("No file loaded."), _("No file."))
        return
    marked_all = ctx.player.toggle_mark_all()
    if marked_all:
        ctx.speak(_("All files marked."), _("All marked."))
    else:
        ctx.speak(_("All files unmarked."), _("All unmarked."))


def clear_marked_files(ctx):
    if ctx.player.clear_marked_files():
        ctx.speak(_("Marked files list cleared."), _("Marks cleared."))
    else:
        ctx.speak(_("No marked files."), _("No marks."))


def announce_marked_files_count(ctx):
    count = ctx.player.get_marked_files_count()
    if count == 1:
        message = _("1 file marked")
    else:
        message = _("{count} files marked").format(count=count)
    ctx.speak(message, message)


def copy_marked_to_folder(ctx):
    _transfer_marked_files(ctx, move=False)


def move_marked_to_folder(ctx):
    _transfer_marked_files(ctx, move=True)


def copy_marked_to_clipboard(ctx):
    files = ctx.player.get_marked_files()
    if not files:
        ctx.speak(_("No marked files."), _("No marks."))
        return
    if set_clipboard_files(files):
        ctx.speak(_("Marked files copied to clipboard."), _("Copied."))
    else:
        ctx.speak(_("Unable to copy marked files to clipboard."), _("Copy failed."))


def delete_marked_files(ctx):
    files = ctx.player.get_marked_files()
    if not files:
        ctx.speak(_("No marked files."), _("No marks."))
        return

    confirm = wx.MessageBox(
        _("Delete {count} marked files?").format(count=len(files)),
        _("Confirm Delete"),
        wx.YES_NO | wx.ICON_WARNING,
        parent=ctx.frame,
    )
    if confirm != wx.YES:
        return

    deleted = []
    failed = []
    current = str(ctx.player.current_path or "")
    current_done = set()
    current_handled = set()
    if current:
        cur_key = os.path.normcase(os.path.abspath(current))
        marked_keys = {
            os.path.normcase(os.path.abspath(path))
            for path in files
            if path
        }
        if cur_key in marked_keys:
            current_handled.add(cur_key)
            ok, _new_path = ctx.player.delete_current_file()
            if ok:
                deleted.append(current)
                current_done.add(cur_key)
            else:
                failed.append(current)

    for path in files:
        key = os.path.normcase(os.path.abspath(path))
        if key in current_handled:
            continue
        try:
            os.remove(path)
            deleted.append(path)
        except OSError:
            failed.append(path)

    if deleted:
        extra = [
            path
            for path in deleted
            if os.path.normcase(os.path.abspath(path)) not in current_done
        ]
        if extra:
            ctx.player.remove_files(extra)
        _refresh_file_loaded_state(ctx)

    if deleted and not failed:
        wx.MessageBox(
            _("Deleted {count} marked files.").format(count=len(deleted)),
            _("Delete Complete"),
            wx.OK | wx.ICON_INFORMATION,
            parent=ctx.frame,
        )
        ctx.speak(_("Marked files deleted."), _("Deleted."))
    elif deleted and failed:
        wx.MessageBox(
            _("Deleted {deleted} files. Failed to delete {failed} files.").format(
                deleted=len(deleted),
                failed=len(failed),
            ),
            _("Delete Complete"),
            wx.OK | wx.ICON_WARNING,
            parent=ctx.frame,
        )
        ctx.speak(_("Some files were deleted."), _("Partial delete."))
    else:
        ctx.speak(_("Could not delete marked files."), _("Delete failed."))


def _transfer_marked_files(ctx, move):
    files = ctx.player.get_marked_files()
    if not files:
        ctx.speak(_("No marked files."), _("No marks."))
        return
    if ctx.frame is None:
        return

    target = _select_target_folder(ctx)
    if not target:
        return

    queue_progress = queue.Queue()
    cancel = _CancelFlag()

    def worker(paths, target_dir):
        transferred = []
        failed = []
        total = len(paths)
        for index, src in enumerate(paths, start=1):
            if cancel.is_set():
                break
            try:
                dst = _resolve_destination_path(target_dir, src)
                if move:
                    shutil.move(src, dst)
                else:
                    shutil.copy2(src, dst)
                transferred.append(src)
            except OSError as exc:
                failed.append((src, str(exc)))
            queue_progress.put((index, total, os.path.basename(src)))
        return {
            "transferred": transferred,
            "failed": failed,
            "cancelled": cancel.is_set(),
        }

    title = _("Moving marked files") if move else _("Copying marked files")
    progress = wx.ProgressDialog(
        title,
        _("Starting..."),
        maximum=len(files),
        parent=ctx.frame,
        style=wx.PD_APP_MODAL | wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE,
    )

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = executor.submit(worker, files, target)
    last_value = 0
    cancelled_by_user = False
    while not future.done() or not queue_progress.empty():
        try:
            value, _total, name = queue_progress.get(timeout=0.05)
            last_value = max(last_value, value)
            keep_going, _skip = progress.Update(
                last_value,
                _("Processing: {name}").format(name=name),
            )
            if not keep_going:
                cancel.set()
                cancelled_by_user = True
                break
        except queue.Empty:
            keep_going, _skip = progress.Pulse(_("Working..."))
            if not keep_going:
                cancel.set()
                cancelled_by_user = True
                break
        wx.YieldIfNeeded()
        time.sleep(0.01)

    if cancelled_by_user:
        try:
            progress.Destroy()
        except Exception:
            pass
        executor.shutdown(wait=False, cancel_futures=False)
        ctx.speak(_("Operation canceled."), _("Canceled."))
        return

    result = future.result()
    executor.shutdown(wait=False, cancel_futures=False)

    try:
        progress.Destroy()
    except Exception:
        pass

    transferred = result["transferred"]
    failed = result["failed"]

    if move and transferred:
        ctx.player.remove_files(transferred)
        _refresh_file_loaded_state(ctx)

    if transferred and not failed:
        wx.MessageBox(
            _("{count} files processed successfully.").format(count=len(transferred)),
            _("Operation Complete"),
            wx.OK | wx.ICON_INFORMATION,
            parent=ctx.frame,
        )
        if move:
            ctx.speak(_("Marked files moved."), _("Moved."))
        else:
            ctx.speak(_("Marked files copied."), _("Copied."))
        return

    if transferred and failed:
        wx.MessageBox(
            _("Processed {ok} files. Failed for {failed} files.").format(
                ok=len(transferred),
                failed=len(failed),
            ),
            _("Operation Complete"),
            wx.OK | wx.ICON_WARNING,
            parent=ctx.frame,
        )
        ctx.speak(_("Operation completed with errors."), _("Partial success."))
        return

    if result["cancelled"]:
        ctx.speak(_("Operation canceled."), _("Canceled."))
    else:
        ctx.speak(_("Operation failed."), _("Failed."))


def _select_target_folder(ctx):
    with wx.DirDialog(
        ctx.frame,
        message="",
        defaultPath=ctx.settings.get_last_dir() or "",
        style=wx.DD_DIR_MUST_EXIST,
    ) as dialog:
        if dialog.ShowModal() == wx.ID_OK:
            folder = dialog.GetPath()
            ctx.settings.set_last_dir(folder)
            return folder
    return None


def _resolve_destination_path(target_dir, source_path):
    base_name = os.path.basename(source_path)
    stem, ext = os.path.splitext(base_name)
    candidate = os.path.join(target_dir, base_name)
    suffix = 1
    while os.path.exists(candidate):
        candidate = os.path.join(target_dir, f"{stem} ({suffix}){ext}")
        suffix += 1
    return candidate


def _refresh_file_loaded_state(ctx):
    has_current = bool(ctx.player.current_path)
    ctx.set_file_loaded(has_current)
    ctx.set_playing(has_current)

