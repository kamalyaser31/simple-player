APP_NAME = "Simple Audio Player"
APP_VERSION = "1.1.0"
DOMAIN = "SimpleAudioPlayer"

CONFIG_FILENAME = "settings.ini"

VOLUME_MIN = 0
VOLUME_MAX = 1000
VOLUME_STEP = 5
VOLUME_MIN_SHORTCUT = 5
SPEED_MIN = 0.5
SPEED_MAX = 4.0
SPEED_STEP = 0.1

APP_UPDATE_REPO_OWNER = "kamalyaser31"
APP_UPDATE_REPO_NAME = "simple-player"
APP_REPO_URL = "https://github.com/" + APP_UPDATE_REPO_OWNER + "/" + APP_UPDATE_REPO_NAME
APP_UPDATE_INFO_URL = (
    "https://raw.githubusercontent.com/"
    + APP_UPDATE_REPO_OWNER
    + "/"
    + APP_UPDATE_REPO_NAME
    + "/main/info.json"
)
APP_UPDATE_RELEASES_URL = (
    "https://github.com/"
    + APP_UPDATE_REPO_OWNER
    + "/"
    + APP_UPDATE_REPO_NAME
    + "/releases/download"
)
APP_UPDATE_ASSET_TEMPLATE = "SimpleAudioPlayer-v{version}.{ext}"
APP_UPDATE_PORTABLE_EXT = "zip"
APP_UPDATE_INSTALLER_EXT = "exe"
APP_UPDATE_UPDATER_EXE = "Updater.exe"
APP_UPDATE_INSTALLER_MARKER = ".sap_installed"

YT_DLP_UPDATE_CHANNELS = ("stable", "nightly", "master")
YT_DLP_DEFAULT_CHANNEL = "stable"

AUDIO_EXTENSIONS = {
    ".aac",
    ".aiff",
    ".alac",
    ".flac",
    ".m4a",
    ".mp3",
    ".mp4",
    ".ogg",
    ".opus",
    ".wav",
    ".wma",
}
