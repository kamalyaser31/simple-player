import ssl
import sys
from urllib import request

try:
    import certifi
except Exception:
    certifi = None


_FROZEN_CONTEXT = None
_FROZEN_CONTEXT_READY = False


def open_url(req, timeout):
    context = _get_frozen_ssl_context()
    if context is None:
        return request.urlopen(req, timeout=timeout)
    return request.urlopen(req, timeout=timeout, context=context)


def _get_frozen_ssl_context():
    global _FROZEN_CONTEXT, _FROZEN_CONTEXT_READY
    if _FROZEN_CONTEXT_READY:
        return _FROZEN_CONTEXT
    _FROZEN_CONTEXT_READY = True

    # Prefer certifi CA bundle in frozen builds where system roots are often missing.
    if not getattr(sys, "frozen", False):
        return None

    cafile = ""
    if certifi is not None:
        try:
            cafile = certifi.where()
        except Exception:
            cafile = ""

    try:
        if cafile:
            _FROZEN_CONTEXT = ssl.create_default_context(cafile=cafile)
        else:
            _FROZEN_CONTEXT = ssl.create_default_context()
    except Exception:
        _FROZEN_CONTEXT = None
    return _FROZEN_CONTEXT
