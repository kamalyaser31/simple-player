"""Download the pinned libmpv build into player/mpv.dll.

mpv.dll (about 120 MB) is over GitHub's 100 MB file limit, so it is not in
git. It lives as a release asset of this repository instead, and this script
fetches it and checks its SHA256. Run from anywhere:

    python player/scripts/fetch_mpv.py
"""

import argparse
import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

MPV_VERSION = "0.42.0"
ASSET_URL = (
    "https://github.com/kamalyaser31/simple-player/releases/download/"
    f"libmpv-{MPV_VERSION}/libmpv-{MPV_VERSION}-x86_64.zip"
)
API_RELEASE_URL = (
    "https://api.github.com/repos/kamalyaser31/simple-player/releases/tags/"
    f"libmpv-{MPV_VERSION}"
)
DLL_SHA256 = "88504ee5560942a955405e99dfb5971368e4cf851321f36565bf2a667271db1b"
DLL_PATH = Path(__file__).resolve().parent.parent / "mpv.dll"


def sha256_of(data):
    return hashlib.sha256(data).hexdigest()


def is_current(path):
    try:
        return sha256_of(path.read_bytes()) == DLL_SHA256
    except OSError:
        return False


def download(url, accept=None):
    req = urllib.request.Request(url)
    if accept:
        req.add_header("Accept", accept)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def download_via_api():
    # Some networks block github.com but reach api.github.com.
    release = json.loads(download(API_RELEASE_URL))
    asset_url = release["assets"][0]["url"]
    return download(asset_url, accept="application/octet-stream")


def fetch(url):
    try:
        archive = download(url)
    except Exception as exc:
        if url != ASSET_URL:
            raise
        print(f"Direct download failed ({exc}); trying the GitHub API.")
        archive = download_via_api()
    with zipfile.ZipFile(io.BytesIO(archive)) as zf:
        return zf.read("mpv.dll")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default=ASSET_URL, help="asset zip to download")
    args = parser.parse_args()

    if is_current(DLL_PATH):
        print(f"mpv.dll {MPV_VERSION} already present.")
        return 0
    try:
        dll = fetch(args.url)
    except Exception as exc:
        print(f"Could not download libmpv: {exc}", file=sys.stderr)
        return 1
    if sha256_of(dll) != DLL_SHA256:
        print("Downloaded mpv.dll failed the SHA256 check.", file=sys.stderr)
        return 1
    DLL_PATH.write_bytes(dll)
    print(f"mpv.dll {MPV_VERSION} written to {DLL_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
