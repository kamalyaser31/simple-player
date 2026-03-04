import wx
from gettext import gettext as _

import speech
from recording import RecOpts


def start_rec(ctx, rec):
    if rec.is_running:
        return
    opts = _build_opts(ctx.settings)
    res = rec.start(opts)
    if not res.get("ok"):
        _error(ctx.frame, _("Could not start recording.\n{error}"), res.get("error"))


def pause_resume_rec(ctx, rec):
    if not rec.is_running:
        return
    if rec.is_paused:
        res = rec.resume()
        if not res.get("ok"):
            _error(ctx.frame, _("Could not resume recording.\n{error}"), res.get("error"))
        return

    res = rec.pause()
    if not res.get("ok"):
        _error(ctx.frame, _("Could not pause recording.\n{error}"), res.get("error"))
        return
    speech.speak(_("paused"))


def stop_rec(ctx, rec):
    if not rec.is_running:
        return
    res = rec.stop(beep=True)
    if not res.get("ok"):
        _error(ctx.frame, _("Could not stop recording.\n{error}"), res.get("error"))


def _build_opts(settings):
    channels = 1 if settings.get_rec_channels() == "mono" else 2
    return RecOpts(
        channels=channels,
        bitrate=settings.get_rec_quality(),
        fmt=settings.get_rec_format(),
        folder=settings.get_rec_folder(),
    )


def _error(parent, template, detail):
    text = str(detail or _("Unknown error.")).strip()
    wx.MessageBox(
        template.format(error=text),
        _("Recording"),
        wx.OK | wx.ICON_ERROR,
        parent=parent,
    )
