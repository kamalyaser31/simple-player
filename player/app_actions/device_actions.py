from gettext import gettext as _

import wx

from ui.sound_cards_dialog import SoundCardDialog


def open_sound_cards(ctx):
    if ctx.frame is None:
        return
    devices = ctx.player.get_audio_devices()
    if not devices:
        ctx.speak(_("No sound cards found."), _("No devices."))
        return
    labels = [desc for _name, desc in devices]
    current = ctx.player.get_audio_device() or ctx.settings.get_audio_device()
    selected = 0
    for idx, (name, _desc) in enumerate(devices):
        if name == current:
            selected = idx
            break
    dialog = SoundCardDialog(ctx.frame, labels, selected)
    if dialog.ShowModal() == wx.ID_OK:
        index = dialog.get_selection()
        if 0 <= index < len(devices):
            name = devices[index][0]
            if ctx.player.set_audio_device(name):
                ctx.settings.set_audio_device(name)
                ctx.settings.save()
                ctx.speak(_("Sound card set."), _("Set."))
            else:
                ctx.speak(_("Could not set sound card."), _("Set failed."))
    dialog.Destroy()
