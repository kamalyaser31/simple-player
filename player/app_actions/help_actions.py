import os
from pathlib import Path
from gettext import gettext as _

import wx

from config.constants import APP_NAME, APP_REPO_URL, APP_VERSION
from config.localization import app_root
from ui.help_dialogs import AboutDialog
from youtube.ui_utils import open_url


TG_URL = "https://t.me/kamalyaser31"
MAIL_URL = "mailto:kamalyaser31@gmail.com"


def open_guide(ctx):
    _open_doc(ctx, "userguide.html")


def open_changes(ctx):
    _open_doc(ctx, "changes.html")


def open_contact(ctx):
    open_contact_website(ctx)


def open_contact_email(ctx):
    _open_link(ctx, MAIL_URL)


def open_contact_tg(ctx):
    _open_link(ctx, TG_URL)


def open_contact_website(ctx):
    _open_link(ctx, APP_REPO_URL)


def show_about(ctx):
    if ctx.frame is None:
        return
    dlg = AboutDialog(
        ctx.frame,
        app_name=APP_NAME,
        version=APP_VERSION,
        website=APP_REPO_URL,
    )
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()


def _open_doc(ctx, name):
    if ctx.frame is None:
        return
    path = _find_doc(name, ctx.settings.get_ui_language())
    if path is None:
        wx.MessageBox(
            _("Could not find the file {name}.").format(name=name),
            _("Error"),
            wx.OK | wx.ICON_WARNING,
            parent=ctx.frame,
        )
        return
    if _open_file(path):
        return
    ctx.speak(_("Could not open the file."), _("Open failed."))


def _open_link(ctx, target):
    if open_url(target):
        return
    ctx.speak(_("Could not open the link."), _("Open failed."))


def _open_file(path):
    target = str(path)
    try:
        os.startfile(target)
        return True
    except Exception:
        pass
    try:
        return bool(Path(target).is_file() and wx.LaunchDefaultBrowser(Path(target).resolve().as_uri()))
    except Exception:
        return False


def _find_doc(name, lang_code):
    root = Path(app_root()) / "docs"
    if not root.is_dir():
        return None

    for code in _codes(lang_code):
        hit = root / code / name
        if hit.is_file():
            return hit

    fallback = root / "en" / name
    if fallback.is_file():
        return fallback

    for folder in sorted(root.iterdir()):
        if not folder.is_dir():
            continue
        hit = folder / name
        if hit.is_file():
            return hit
    return None


def _codes(lang_code):
    out = []
    text = str(lang_code or "").strip()
    if text and text.lower() not in ("system", "default"):
        _push_lang(out, text)
        return out

    try:
        info = wx.Locale.GetLanguageInfo(wx.Locale.GetSystemLanguage())
    except Exception:
        info = None
    if info is not None:
        canon = str(getattr(info, "CanonicalName", "") or "").strip()
        if canon:
            _push_lang(out, canon)
            return out
    _push_lang(out, "en")
    return out


def _push_lang(out, text):
    raw = str(text or "").strip()
    if not raw:
        return
    picks = [
        raw,
        raw.lower(),
        raw.replace("-", "_"),
        raw.replace("-", "_").lower(),
        raw.split("-")[0],
        raw.split("_")[0],
    ]
    for item in picks:
        value = str(item or "").strip()
        if value and value not in out:
            out.append(value)
