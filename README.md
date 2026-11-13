[العربية](README.ar.md)

# Simple Audio Player

Simple Audio Player is an accessible audio player for Windows, built with Python, wxPython and libmpv.
It is made for people who use a screen reader such as NVDA: every action has a keyboard shortcut, and the app speaks its own status messages.
It plays local files, folders, web streams and YouTube.

## Features

- Keyboard control for everything, with shortcuts you can change, and global shortcuts that work from any program.
- Beginner and Advanced spoken verbosity.
- Playback of audio files, folders and stream links; speed and volume (up to 1000%) control; A-B loop; bookmarks; marked-file copy, move and delete.
- Audio filters: loudness normalization with a limiter, mono playback, and silence removal.
- YouTube search, links, playlists, favorites, and audio download as M4A.
- YouTube subscriptions without a Google account: follow channels and playlists, and press Ctrl+U for the newest videos of your channels (up to 50, Shorts left out).
- Recording from the default input device to WAV or MP3.
- Windows media keys, Explorer integration ("Play with Simple Audio Player"), and automatic update checks.

## Installation

Download a file from the [releases page](https://github.com/kamalyaser31/simple-player/releases):

- `SimpleAudioPlayer-v<version>.exe` is the installer. It installs for the current Windows user without administrator rights, by default into `%LOCALAPPDATA%\Programs\Simple Audio Player`.
- `SimpleAudioPlayer-v<version>.zip` is the portable version. Extract it and run `SimpleAudioPlayer.exe`.

The YouTube components `yt-dlp.exe` and `deno.exe` are not in the release files. The app offers to download them the first time it starts.

## User guide

The full guide is in [player/docs/en/userguide.html](player/docs/en/userguide.html). In the app, press F1. The list of changes is in [CHANGELOG.md](CHANGELOG.md).

## Build and run from source

You need Windows and Python 3.11 (the release workflow uses 3.11). Inno Setup 6 is needed only for the installer.

Install the requirements from the repository root:

```powershell
pip install -r player/requirements.txt
```

Run the app from the `player` folder:

```powershell
cd player; python SimpleAudioPlayer.py
```

Build the standalone folder with PyInstaller, from the `player` folder (install it first with `pip install pyinstaller`):

```powershell
python -m PyInstaller --noconfirm SimpleAudioPlayer.spec
```

Build the installer with Inno Setup, from the repository root, after the folder above exists:

```powershell
iscc player/simple_audio_player.iss
```

Run the whole local release build, which also builds `Updater.exe` and downloads `mpv.dll`:

```powershell
.\build_test.ps1
```

## Contributing

Contributions are welcome. Please open an issue first to agree on the change.
Before a pull request, check that the version, file types, translations and packaging files agree:

```powershell
python scripts/validate_project_consistency.py
```

Run it from the `player` folder. Report problems at [GitHub Issues](https://github.com/kamalyaser31/simple-player/issues).

## بيانات المطور (Developer Details)

- **المطور:** كمال ياسر (Kamal Yaser)
- **البريد الإلكتروني:** [kamalyaser31@gmail.com](mailto:kamalyaser31@gmail.com)
- **تيليجرام:** [@kamalyaser31](https://t.me/kamalyaser31)

---

## رخصة الاستخدام (License)

يخضع هذا المشروع لشروط رخصة MIT License مفتوحة المصدر.
