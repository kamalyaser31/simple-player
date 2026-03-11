import wx
from gettext import gettext as _
import traceback

from ui.yt_dialogs import ResultsDlg

from .search import load_more as search_more
from .state import clear_ses, get_ses
from .ui_utils import copy_text, open_url, res_label
from .video import dl_url


def show_res(ctx, ses, sel, prefetch, play_item, pool, prefetch_n):
    items = ses.get("items", [])
    if not items:
        ctx.speak(_("No videos were found."), _("No videos found."))
        return

    cur_sel = int(sel)
    while True:
        dlg = ResultsDlg(ctx.frame, _("Videos"), "")
        busy_more = {"on": False}
        try:
            _set_res(dlg, ses)
            if 0 <= cur_sel < dlg.list_box.GetCount():
                dlg.list_box.SetSelection(cur_sel)

            # Search results should keep prefetching in the background.
            prefetch(ses, 0, prefetch_n)

            action = {"kind": "close", "idx": max(0, cur_sel)}

            def cur_idx():
                idx = dlg.get_selection()
                return idx if idx != wx.NOT_FOUND else 0

            def do_play(_event=None):
                if dlg.list_box.GetCount() <= 0:
                    return
                action["kind"] = "play"
                action["idx"] = cur_idx()
                dlg.EndModal(wx.ID_OK)

            def do_close(_event=None):
                action["kind"] = "close"
                action["idx"] = cur_idx()
                dlg.EndModal(wx.ID_CANCEL)

            def do_dl(_event=None):
                if dlg.list_box.GetCount() <= 0:
                    return
                dl_url(ctx, ses["items"][cur_idx()].url)

            def do_copy(_event=None):
                if dlg.list_box.GetCount() <= 0:
                    return
                item = ses["items"][cur_idx()]
                if copy_text(item.url):
                    ctx.speak(_("Link copied."), _("Copied."))
                else:
                    ctx.speak(_("Could not copy link."), _("Copy failed."))

            def do_browser(_event=None):
                if dlg.list_box.GetCount() <= 0:
                    return
                item = ses["items"][cur_idx()]
                if not open_url(item.url):
                    ctx.speak(_("Could not open browser."), _("Browser open failed."))

            def do_channel(_event=None):
                if dlg.list_box.GetCount() <= 0:
                    return
                item = ses["items"][cur_idx()]
                url = str(item.channel_url or "").strip()
                if not url:
                    ctx.speak(_("Channel link is not available."), _("No channel link."))
                    return
                if not open_url(url):
                    ctx.speak(_("Could not open browser."), _("Browser open failed."))

            def on_pick(_event=None):
                idx = cur_idx()
                action["idx"] = idx
                prefetch(ses, idx + 1, prefetch_n)
                if idx == dlg.list_box.GetCount() - 1:
                    _try_more(ctx, ses, dlg, busy_more, prefetch, pool, prefetch_n)

            dlg.play_btn.Bind(wx.EVT_BUTTON, do_play)
            dlg.close_btn.Bind(wx.EVT_BUTTON, do_close)
            dlg.download_btn.Bind(wx.EVT_BUTTON, do_dl)
            dlg.list_box.Bind(wx.EVT_LISTBOX_DCLICK, do_play)
            dlg.list_box.Bind(wx.EVT_LISTBOX, on_pick)
            dlg.list_box.Bind(wx.EVT_CONTEXT_MENU, lambda _e: dlg.show_menu())
            dlg.Bind(wx.EVT_MENU, do_copy, id=dlg.id_copy)
            dlg.Bind(wx.EVT_MENU, do_browser, id=dlg.id_browser)
            dlg.Bind(wx.EVT_MENU, do_channel, id=dlg.id_channel)
            dlg.Bind(wx.EVT_MENU, do_dl, id=dlg.id_dl)
            dlg.Bind(wx.EVT_MENU, do_play, id=dlg.id_play)
            dlg.ShowModal()
        finally:
            dlg.Destroy()

        if action["kind"] == "play":
            idx = int(action["idx"])
            if idx < 0 or idx >= len(ses["items"]):
                idx = 0
            if play_item(ctx, ses["items"][idx], ses=ses, idx=idx):
                return
            cur_sel = idx
            continue

        clear_ses(ctx)
        return


def _set_res(dlg, ses):
    labels = [item.title for item in ses.get("items", [])]
    dlg.set_label(res_label(ses))
    dlg.set_items(labels)


def _try_more(ctx, ses, dlg, busy, prefetch, pool, prefetch_n):
    if busy["on"]:
        return
    if str(ses.get("kind") or "") != "search":
        return
    st = ses.get("search")
    if st is None or not st.has_more():
        return
    cancel = ses.get("cancel")
    if cancel is not None and cancel.is_set():
        return
    jobs = ses.setdefault("more_jobs", {})
    key = str(getattr(st, "cont", "") or "")
    existing = jobs.get(key)
    if existing is not None and not existing.done():
        return

    busy["on"] = True
    ctx.speak(_("Loading more videos..."), _("Loading more videos..."))
    fut = pool.submit(search_more, st, cancel)
    jobs[key] = fut

    def done(_future):
        jobs.pop(key, None)
        wx.CallAfter(_more_done, ctx, ses, dlg, busy, _future, prefetch, prefetch_n)

    fut.add_done_callback(done)


def _more_done(ctx, ses, dlg, busy, future, prefetch, prefetch_n):
    busy["on"] = False
    cur = get_ses(ctx)
    if cur is None or cur is not ses:
        return
    cancel = ses.get("cancel")
    if cancel is not None and cancel.is_set():
        return
    try:
        new_items = list(future.result() or [])
    except Exception:
        traceback.print_exc()
        return
    if not new_items:
        return
    ses["items"].extend(new_items)
    ses["urls"].update(str(item.url or "") for item in new_items)
    try:
        dlg.append_items([item.title for item in new_items])
        dlg.set_label(res_label(ses))
    except Exception:
        traceback.print_exc()
        return
    start = len(ses["items"]) - len(new_items)
    prefetch(ses, start, prefetch_n)
