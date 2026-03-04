from gettext import gettext as _

import speech
import wx

from config.constants import VOLUME_MAX, VOLUME_MIN_SHORTCUT
from helpers.utils import format_time
from ui import dialogs
from youtube.state import is_yt

SEEK_STEP_PRESETS = {
    "1": 1,
    "2": 5,
    "3": 60,
    "4": 300,
    "5": 600,
    "6": 1200,
    "7": 1800,
    "8": 2400,
    "9": 3000,
    "0": 3600,
}

SEEK_STEP_LABELS = {
    "1": _("1 second"),
    "2": _("5 seconds"),
    "3": _("1 minute"),
    "4": _("5 minutes"),
    "5": _("10 minutes"),
    "6": _("20 minutes"),
    "7": _("30 minutes"),
    "8": _("40 minutes"),
    "9": _("50 minutes"),
    "0": _("60 minutes"),
    "-": _("Custom value"),
}

DEFAULT_SEEK_STEP = 5.0


def toggle_play_pause(ctx):
    if not ctx.player.current_path:
        ctx.speak(_("No file loaded."), _("No file."))
        return

    # If the player is stopped (no duration), but we have a current file,
    # then reload and play it from the start.
    if ctx.player.get_duration() is None:
        if ctx.player.reload_current_file():
            ctx.set_playing(True)
            if not ctx.is_advanced():
                speech.speak(_("Play"))
        return

    is_playing = ctx.player.toggle_pause()
    ctx.set_playing(is_playing)
    if not ctx.is_advanced():
        speech.speak(_("Play") if is_playing else _("Pause"))


def toggle_verbosity(ctx):
    current = ctx.settings.get_verbosity()
    if current == "advanced":
        next_value = "beginner"
        message = _("Beginner mode")
    else:
        next_value = "advanced"
        message = _("Advanced mode")
    ctx.settings.set_verbosity(next_value)
    ctx.settings.save()
    speech.speak(message)


def toggle_shuffle(ctx):
    if not ctx.player.current_path:
        ctx.speak(_("No file loaded."), _("No file."))
        return
    if is_yt(ctx.player.current_source):
        ctx.player.set_shuffle_enabled(False)
        if ctx.frame is not None:
            ctx.frame.set_shuffle_checked(False)
        ctx.speak(
            _("Shuffle is disabled for YouTube streams."),
            _("Shuffle disabled for YouTube."),
        )
        return
    enabled = ctx.player.toggle_shuffle()
    if ctx.frame is not None:
        ctx.frame.set_shuffle_checked(enabled)
    if enabled:
        ctx.speak(_("Shuffle on"), _("Shuffle on"))
    else:
        ctx.speak(_("Shuffle off"), _("Shuffle off"))


def toggle_repeat_file(ctx):
    if not ctx.player.current_path:
        ctx.speak(_("No file loaded."), _("No file."))
        return
    enabled = ctx.player.toggle_repeat_file()
    if ctx.frame is not None:
        ctx.frame.set_repeat_file_checked(enabled)
    if enabled:
        ctx.speak(_("Repeat on"), _("Repeat on"))
    else:
        ctx.speak(_("Repeat off"), _("Repeat off"))


def toggle_silence_removal(ctx):
    enabled, success = ctx.player.toggle_silence_removal()
    if not success:
        ctx.speak(_("Could not change silence removal filter."), _("Filter failed."))
        return
    ctx.settings.set_silence_removal_enabled(enabled)
    ctx.settings.save()
    if ctx.frame is not None:
        ctx.frame.set_silence_removal_checked(enabled)
    if enabled:
        ctx.speak(_("Silence removal on"), _("Silence removal on"))
    else:
        ctx.speak(_("Silence removal off"), _("Silence removal off"))


def seek_backward(ctx):
    _seek_by_multiplier(ctx, -1.0)


def seek_forward(ctx):
    _seek_by_multiplier(ctx, 1.0)


def seek_backward_x2(ctx):
    _seek_by_multiplier(ctx, -2.0)


def seek_forward_x2(ctx):
    _seek_by_multiplier(ctx, 2.0)


def seek_backward_x4(ctx):
    _seek_by_multiplier(ctx, -4.0)


def seek_forward_x4(ctx):
    _seek_by_multiplier(ctx, 4.0)


def seek_backward_x8(ctx):
    _seek_by_multiplier(ctx, -8.0)


def seek_forward_x8(ctx):
    _seek_by_multiplier(ctx, 8.0)


def seek_start(ctx):
    loop = _active_ab(ctx)
    if loop is not None:
        ctx.player.seek_absolute(loop["start"])
        return
    ctx.player.seek_absolute(0)


def seek_end(ctx):
    loop = _active_ab(ctx)
    if loop is not None:
        ctx.player.seek_absolute(loop["end"])
        return
    if not ctx.player.seek_to_end():
        ctx.speak(_("Time not available"), _("Unavailable"))


def change_volume(ctx, delta):
    volume = ctx.player.change_volume(delta)
    ctx.settings.set_volume(volume)
    ctx.announce_volume_value(volume, _("Volume {volume} percent"))


def set_volume_max(ctx):
    volume = ctx.player.set_volume(VOLUME_MAX)
    ctx.settings.set_volume(volume)
    ctx.announce_volume_value(volume, _("Volume {volume} percent"))


def set_volume_min(ctx):
    volume = ctx.player.set_volume(VOLUME_MIN_SHORTCUT)
    ctx.settings.set_volume(volume)
    ctx.announce_volume_value(volume, _("Volume {volume} percent"))


def announce_volume(ctx):
    volume = ctx.player.get_volume()
    if ctx.is_advanced():
        speech.speak(f"{str(int(volume))}%")
    else:
        speech.speak(_("Volume is {percent}%").format(percent=int(volume)))


def announce_elapsed(ctx):
    _announce_time(ctx, _("Elapsed time: "), ctx.player.get_elapsed())


def announce_remaining(ctx):
    _announce_time(ctx, _("Remaining time: "), ctx.player.get_remaining())


def announce_duration(ctx):
    _announce_time(ctx, _("Total time: "), ctx.player.get_duration())


def announce_percent(ctx):
    duration = ctx.player.get_duration()
    elapsed = ctx.player.get_elapsed()
    if duration is None or elapsed is None or duration <= 0:
        ctx.speak(_("Percentage not available"), _("Unavailable"))
        return
    percent = int((elapsed / duration) * 100)
    percent = max(0, min(100, percent))
    ctx.speak(_("{percent} percent").format(percent=percent), f"{percent}%")


def announce_speed(ctx):
    speed = ctx.player.get_speed()
    speed_text = _format_speed(speed)
    speech.speak(_("{speed}x").format(speed=speed_text))


def reset_speed(ctx):
    speed = ctx.player.set_speed(1.0)
    ctx.settings.set_speed(speed)
    speed_text = _format_speed(speed)
    speech.speak(_("{speed}x").format(speed=speed_text))


def change_speed(ctx, delta):
    speed = ctx.player.change_speed(delta)
    ctx.settings.set_speed(speed)
    speed_text = _format_speed(speed)
    speech.speak(_("{speed}x").format(speed=speed_text))


def jump_to_percent(ctx, percent):
    duration = ctx.player.get_duration()
    if duration is None or duration <= 0:
        ctx.speak(_("Time not available"), _("Unavailable"))
        return
    if percent >= 100:
        ctx.player.seek_to_end()
    else:
        target = duration * (percent / 100.0)
        ctx.player.seek_absolute(target)
    ctx.speak(_("{percent} percent").format(percent=percent), f"{percent}%")


def go_to_time(ctx):
    if ctx.frame is None:
        return
    duration = ctx.player.get_duration()
    if duration is None or float(duration) <= 0:
        wx.MessageBox(
            _("Time is not available for the current file."),
            _("Go to time"),
            wx.OK | wx.ICON_WARNING,
            parent=ctx.frame,
        )
        return

    elapsed = ctx.player.get_elapsed()
    try:
        initial = int(max(0, float(elapsed or 0.0)))
    except (TypeError, ValueError):
        initial = 0
    dlg = dialogs.GoToTimeDialog(ctx.frame, duration_seconds=duration, initial_seconds=initial)
    try:
        if dlg.ShowModal() == wx.ID_OK:
            ctx.player.seek_absolute(dlg.get_seconds())
    finally:
        dlg.Destroy()


def set_seek_step(ctx, key):
    ctx.settings.set_seek_step_key(key)
    ctx.settings.save()
    label = SEEK_STEP_LABELS.get(key, "")
    if label:
        speech.speak(label)


def start_selection(ctx):
    if not ctx.player.current_path:
        ctx.speak(_("No file loaded."), _("No file."))
        return
    elapsed = ctx.player.get_elapsed()
    if elapsed is None:
        ctx.speak(_("Time not available"), _("Unavailable"))
        return
    ctx.selection_start = float(elapsed)
    ctx.selection_end = None
    ctx.selection_path = str(ctx.player.current_path or "")
    ctx.player.set_loop_start(ctx.selection_start)
    formatted = format_time(ctx.selection_start)
    ctx.speak(
        _("Start selection: {time}").format(time=formatted),
        _("Start {time}").format(time=formatted),
    )


def end_selection(ctx):
    if not ctx.player.current_path:
        ctx.speak(_("No file loaded."), _("No file."))
        return
    loop = _active_ab(ctx, require_end=False)
    if loop is None:
        ctx.speak(_("Start selection not set."), _("No start."))
        return
    elapsed = ctx.player.get_elapsed()
    if elapsed is None:
        ctx.speak(_("Time not available"), _("Unavailable"))
        return
    end_time = float(elapsed)
    if end_time <= loop["start"]:
        ctx.speak(_("End selection must be after start."), _("Invalid end."))
        return
    if not ctx.player.set_loop_end(end_time):
        ctx.speak(_("Time not available"), _("Unavailable"))
        return
    ctx.selection_end = end_time
    formatted = format_time(end_time)
    ctx.speak(
        _("End selection: {time}").format(time=formatted),
        _("End {time}").format(time=formatted),
    )
    ctx.player.seek_absolute(loop["start"])
    ctx.player.play()


def clear_selection(ctx):
    if _active_ab(ctx) is None:
        ctx.speak(_("No selection to clear."), _("No selection."))
        return
    ctx.player.clear_loop()
    ctx.player.seek_absolute(ctx.selection_end)
    ctx.player.play()
    ctx.reset_selection(clear_loop=False)
    if not ctx.is_advanced():
        speech.speak(_("Selection cleared"))


def _announce_time(ctx, label, seconds):
    formatted = format_time(seconds)
    if formatted is None:
        ctx.speak(_("Time not available"), _("Unavailable"))
    else:
        if ctx.is_advanced():
            speech.speak(formatted)
        else:
            speech.speak(f"{label} {formatted}")


def _get_seek_step_seconds(ctx):
    key = ctx.settings.get_seek_step_key()
    if key == "-":
        value = ctx.settings.get_seek_step_custom()
        if value <= 0:
            return DEFAULT_SEEK_STEP
        return float(value)
    if key in SEEK_STEP_PRESETS:
        return float(SEEK_STEP_PRESETS[key])
    return DEFAULT_SEEK_STEP


def _format_speed(speed):
    try:
        value = float(speed)
    except (TypeError, ValueError):
        return "1"
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _active_ab(ctx, require_end=True):
    current = str(ctx.player.current_path or "")
    if not current:
        return None
    if str(ctx.selection_path or "") != current:
        return None
    start = ctx.selection_start
    end = ctx.selection_end
    if start is None:
        return None
    if require_end and end is None:
        return None
    if end is not None and float(end) <= float(start):
        return None
    return {
        "start": float(start),
        "end": float(end) if end is not None else None,
    }


def _seek_within_selection(ctx, delta):
    loop = _active_ab(ctx)
    if loop is None:
        return False
    elapsed = ctx.player.get_elapsed()
    if elapsed is None:
        return False
    target = float(elapsed) + float(delta)
    target = max(loop["start"], min(loop["end"], target))
    ctx.player.seek_absolute(target)
    return True


def _seek_by_multiplier(ctx, scale):
    seconds = _get_seek_step_seconds(ctx) * abs(float(scale))
    signed = seconds if scale >= 0 else -seconds
    if _seek_within_selection(ctx, signed):
        return
    ctx.player.seek(signed)

