import gettext
import os
import sys
import builtins

import wx

from config.constants import DOMAIN


def app_root():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def locale_dir():
    return os.path.join(app_root(), "locale")


def available_languages():
    root = locale_dir()
    found = []
    if os.path.isdir(root):
        for entry in sorted(os.listdir(root)):
            lang = str(entry or "").strip()
            if not lang:
                continue
            mo_path = os.path.join(root, lang, "LC_MESSAGES", f"{DOMAIN}.mo")
            if os.path.isfile(mo_path):
                found.append(lang)
    return found


def language_name(code):
    text = str(code or "").strip()
    if not text:
        return "System default"
    lookup = text
    info = wx.Locale.FindLanguageInfo(lookup)
    if info is None:
        lookup = text.replace("-", "_")
        info = wx.Locale.FindLanguageInfo(lookup)
    if info is None:
        lookup = text.replace("_", "-")
        info = wx.Locale.FindLanguageInfo(lookup)
    if info is not None:
        desc = str(getattr(info, "Description", "") or "").strip()
        if desc:
            return desc
    return text


class Localization:
    def __init__(self):
        self.locale = None
        self._translator = gettext.NullTranslations()

    def init(self, language_code="system"):
        root = locale_dir()
        selected = str(language_code or "system").strip()
        use_default = selected.lower() in ("", "system", "default")
        if use_default:
            os.environ.pop("LANGUAGE", None)
        else:
            os.environ["LANGUAGE"] = selected

        if use_default:
            self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        else:
            info = wx.Locale.FindLanguageInfo(selected) or wx.Locale.FindLanguageInfo(
                selected.replace("-", "_")
            )
            if info is not None:
                self.locale = wx.Locale(info.Language)
            else:
                self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)

        if os.path.isdir(root):
            self.locale.AddCatalogLookupPathPrefix(root)
            self.locale.AddCatalog(DOMAIN)
        kwargs = {"fallback": True}
        if not use_default:
            kwargs["languages"] = [selected]
        self._translator = gettext.translation(
            DOMAIN,
            localedir=root,
            **kwargs,
        )
        gettext.bindtextdomain(DOMAIN, root)
        gettext.textdomain(DOMAIN)
        gettext.gettext = self._translator.gettext
        gettext.ngettext = self._translator.ngettext
        builtins._ = self._translator.gettext
        self._rebind_loaded_modules()
        return self._translator.gettext

    @property
    def gettext(self):
        return self._translator.gettext

    def _rebind_loaded_modules(self):
        for module in list(sys.modules.values()):
            if module is None:
                continue
            try:
                value = getattr(module, "_", None)
            except Exception:
                continue
            if not callable(value):
                continue
            mod = str(getattr(value, "__module__", "") or "")
            name = str(getattr(value, "__name__", "") or "")
            if mod == "gettext" and name == "gettext":
                try:
                    setattr(module, "_", self._translator.gettext)
                except Exception:
                    continue

