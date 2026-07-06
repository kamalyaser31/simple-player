# Simple Audio Player

Simple Audio Player is a Windows desktop media player built with Python and wxPython.  
The project focuses on practical daily playback, strong keyboard support, and good screen reader compatibility.

It is designed for users who want a straightforward player that still includes advanced tools when needed: playlist and file navigation, YouTube workflows, bookmarks and favorites, recording, and configurable audio behavior.

## Features

Simple Audio Player supports common audio and video formats and includes:

- Keyboard-first control with customizable shortcuts
- Accessible UI and screen reader friendly behavior
- File/folder playback and playlist navigation
- Bookmarks and favorite links (video, playlist, combined YouTube links, and generic streams)
- YouTube search, playback, and download workflows (after components are available)
- Recording with configurable format, bitrate, and output folder
- Audio controls such as normalization, mono downmix, speed control, and silence removal
- Backup/restore support for settings and bookmark data

The app is Windows-focused and integrates with system behaviors such as file association actions and media session controls.

## Download

Prebuilt versions are available on the project releases page:

<https://github.com/kamalyaser31/simple-player/releases>

You can choose either:

- Installer build (`SimpleAudioPlayerSetup.exe`) for regular installation
- Portable ZIP build if you want to run it without installing

If you only want to use the app, downloading from releases is the easiest path.

## Build From Source

### Requirements

For local development/build:

- Windows
- Python 3.11 or newer recommended
- Git
- A working C/C++ build environment may be needed for some Python packages depending on your setup

### Clone and run

```powershell
git clone https://github.com/kamalyaser31/simple-player.git
cd simple-player\player
```

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py SimpleAudioPlayer.py
```

### Build executable

```powershell
py -m PyInstaller SimpleAudioPlayer.spec
```

The generated executable is placed in the standard PyInstaller output directory (`dist`).

### Build installer

The repository includes an Inno Setup script:

`player/simple_audio_player.iss`

Use Inno Setup to compile this script when you need an installer package.

## Project Notes

YouTube support depends on runtime components (for example `yt-dlp`) that the app can manage through its own update/download flow.  
For local file playback and normal player features, no special YouTube setup is required.

Application settings are stored in the user profile config path. Feature-specific data (such as bookmarks, favorites, and position data) is stored in separate JSON files in the same settings directory.

## Contributing

Contributions are welcome.

If you want to contribute, please open an issue first for bugs or feature ideas, especially for behavior changes. This keeps implementation direction clear before code review.

For pull requests, prefer focused changes with clear scope. Include:

- What changed
- Why it changed
- How you tested it (manual steps and/or automated checks)

Please avoid unrelated refactors in the same pull request unless they are required for the feature.

## Contact Us

If you have any questions or ideas, you can contact us through the following ways:

- Email: `kamalyaser31@gmail.com`
- Telegram: <https://t.me/kamalyaser31>

For issues and feature request, please go to:

<https://github.com/kamalyaser31/simple-player/issues>

## License

This project is licensed under the **GNU General Public License, version 2, or (at your option) any later version** (GPL-2.0-or-later).

See [LICENSE](LICENSE) for the full license text.
