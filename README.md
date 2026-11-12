# Simple Audio Player

Simple Audio Player is an accessible, Windows-focused desktop media player built with Python, wxPython, and libmpv. Designed with keyboard-first controls and screen-reader compatibility in mind, it provides a straightforward interface that hides advanced audio filters, YouTube workflows, and comprehensive session management under the hood.

---

## Table of Contents

- [Core Features](#core-features)
  - [1. Keyboard-First & Accessible UX](#1-keyboard-first--accessible-ux)
  - [2. Advanced Audio Processing & FFmpeg Filters](#2-advanced-audio-processing--ffmpeg-filters)
  - [3. YouTube Search, Playback, & Prefetching](#3-youtube-search-playback--prefetching)
  - [4. Audio Recording Engine](#4-audio-recording-engine)
  - [5. Bookmarks, Favorites, & Atomic Storage](#5-bookmarks-favorites--atomic-storage)
- [Windows Shell Integration](#windows-shell-integration)
- [Build and Run From Source](#build-and-run-from-source)
  - [Requirements](#requirements)
  - [1. Clone and Run](#1-clone-and-run)
  - [2. Build Executable](#2-build-executable)
  - [3. Build Installer](#3-build-installer)
  - [4. Local Build Testing](#4-local-build-testing)
- [Project Architecture Notes](#project-architecture-notes)
- [Contact and Contributing](#contact-and-contributing)
- [License](#license)

---

## Core Features

### 1. Keyboard-First & Accessible UX
Simple Audio Player is designed for high accessibility, integrating directly with screen readers (via `accessible_output3`) and featuring:
- **Dual-Mode Spoken Verbosity**: Toggles between beginner and advanced spoken feedback. Text-to-speech reads descriptive instructions or concise status updates based on the active mode.
- **Multi-Press Information Cycles**: Pressing the File Info key multiple times within 0.3 seconds escalates the detail announced:
  1. *First Press*: Announces the active filename.
  2. *Second Press*: Announces the absolute folder path.
  3. *Third Press*: Copies the absolute file path directly to the Windows clipboard.
- **Deduplicated Global Hotkeys**: Uses a background keyboard hook (`pynput`) that deduplicates key-repeat events when physical keys are held down.

### 2. Advanced Audio Processing & FFmpeg Filters
Using FFmpeg's `lavfi` (Libavfilter) graph interface via `libmpv`, the player handles audio enhancement dynamically:
- **Normalization & Limiting**: Enabled via `dynaudnorm` and `alimiter` filters to ensure balanced levels without clipping.
- **Preamplification (up to 1000%)**: For volume levels $\le 100\%$, standard hardware volume is scaled. For volume values between $100\%$ and $1000\%$, the hardware master volume is locked at $100\%$, and a pre-amplification gain filter (`lavfi=[volume=gain]`) scales the audio source continuously up to $10.0\times$ gain.
- **Mono Downmixing**: Downmixes multi-channel audio to mono (`aformat=channel_layouts=mono`).
- **Silence Removal**: Automatically strips silence during playback based on peak/RMS noise thresholds.

### 3. YouTube Search, Playback, & Prefetching
The player embeds a powerful YouTube resolver with optimization features:
- **3-Tier Link Resolution**: Resolves YouTube links via a nested fallback strategy using `yt-dlp` (standard dump, URL extraction, and general fallback).
- **Background Prefetch Pipeline**: To eliminate track-switching latency, the player spawns a background thread pool (`_PREP_POOL`) to resolve and cache up to 200 upcoming streams while the active track plays. If a cached stream is next, playback starts instantly; otherwise, it plays a "Loading next video..." speech cue.
- **Subscriptions Without a Google Account**: Follow channels and save playlists locally (`subscriptions.json` next to the settings file). Add one by pasting a channel or playlist link (File > YouTube subscriptions..., `Ctrl+Shift+U`) or with `Ctrl+S` on a search result. `Ctrl+U` lists the 50 newest videos of all followed channels, Shorts excluded, each read as title, channel and age. Videos come from YouTube's public RSS feeds, so no sign-in is needed.
- **Component Self-Updater**: Automatically monitors, downloads, and updates runtime dependencies (`yt-dlp.exe` and `deno.exe`) directly from remote repository releases.

### 4. Audio Recording Engine
A dedicated recording subsystem (`RecEngine`) allows users to record active playback or microphone feeds:
- Supports real-time encoding into multiple formats (e.g., MP3, M4A, WAV).
- Customizable sample rates, bitrates, and dedicated output directories.

### 5. Bookmarks, Favorites, & Atomic Storage
- **Atomic Database Writes**: To prevent data corruption on sudden shutdowns, settings and playlists are written to a temporary file, flushed to disk, and then replaced atomically (`os.replace`).
- **Bookmark Slots**: Allows quick-saving and jumping to precise positional bookmarks using keyboard slot mappings.
- **Favorites Store**: Categorizes saved links into lists for videos, playlists, combined YouTube URLs, and generic network streams.

---

## Windows Shell Integration

The player integrates deeply with Windows system behaviors:
- **ProgID Registry Association**: Registers as `SimpleAudioPlayer.media` under user classes (`HKCU\Software\Classes`).
- **Explorer Context Menu**: Adds a native `"Play with Simple Audio Player"` shortcut for supported files.
- **Shell Change Notification**: Calls `SHChangeNotify` to immediately refresh file type icons across Windows Explorer upon association.
- **System Media Transport Controls (SMTC)**: Synchronizes track details, duration, timeline sliders, and system media keys (Play, Pause, Next, Previous) with Windows OS using `winsdk` API.

---

## Build and Run From Source

### Requirements
- Windows OS (7, 10, or 11)
- Python 3.11 (highly recommended; launcher `py` handles version routing)
- Git
- Inno Setup 6 (optional, required to compile the installer package)

### 1. Clone and Run
Clone the repository and install requirements inside a Python virtual environment:
```powershell
git clone https://github.com/kamalyaser31/simple-player.git
cd simple-player
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r player/requirements.txt
cd player
python SimpleAudioPlayer.py
```

### 2. Build Executable
Compile the standalone executable folder structure using PyInstaller:
```powershell
python -m PyInstaller SimpleAudioPlayer.spec
```
The output directory will be created inside `player/dist/SimpleAudioPlayer/`.

### 3. Build Installer
To build the setup installer, compile the Inno Setup script:
`player/simple_audio_player.iss` using Inno Setup compiler (`ISCC.exe`).

### 4. Local Build Testing
You can run the provided local test script to validate compilation, PyInstaller settings, and WinRT patch application on your Windows machine:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\build_test.ps1
```

---

## Project Architecture Notes

Simple Audio Player utilizes **Composition over Inheritance** through functional mixins to avoid monolithic classes. Key architectural layers are divided as:
- **View (`ui/`)**: Stateless interface layers built with `wxPython` that capture input events and dispatch command tokens to the controller.
- **Controller (`core/controller.py`)**: The central routing hub that coordinates actions between the UI, MPV playback engine, SMTC, and recording subsystems.
- **Model (`core/player/` & `playlist/`)**: Encapsulates the media player playback state and playlist operations.
- **Scripts (`scripts/`)**: Automation utilities for maintenance and deployment:
  * **Version Synchronization (`update_version.py` / `update_version.bat`)**:
    * *Function*: Automatically updates and synchronizes the application version number across all critical files: the root `info.json` (the `"version"` key), the Python constants file `player/config/constants.py` (the `APP_VERSION` variable), and the Windows installer script `player/simple_audio_player.iss` (the `MyAppVersion` definition).
    * *Usage*: Run `python update_version.py <version>` or execute `update_version.bat` which prompts for the version string interactively. The version must be `MAJOR.MINOR.PATCH` (a leading `v` is dropped). After writing, the script runs `validate_project_consistency.py` and exits with its result.
  * **Translation Update (`update_pot.py` / `update_pot.bat`)**:
    * *Function*: Scans all Python source files recursively, extracts translatable string literals wrapped in the `_()` gettext function (ignoring dependency directories like virtual environments and build outputs), and updates the Gettext template file (`player/locale/simple_audio_player.pot`). It then merges the template into every `.po` catalog under `player/locale/` and compiles each `.mo` file. Requires `xgettext`, `msgmerge`, and `msgfmt` in the system path.
    * *Usage*: Run `python update_pot.py` or double-click `update_pot.bat`. Add `--pot-only` to update the template alone.
  * **Consistency Check (`validate_project_consistency.py`)**:
    * *Function*: Checks that the version, file extensions, translation catalogs, packaging files, and release asset names agree across the project.
    * *Usage*: Run `python scripts/validate_project_consistency.py`; it prints each mismatch and exits with code 1 if any is found.
  * **Updater Compilation (`build_updater.bat`)**:
    * *Function*: Automates compiling the standalone self-updater utility (`Updater.exe`) from `player/updater/main.py` using PyInstaller.
    * *Output*: Builds a single-file, windowed executable placed at `player/dist/Updater.exe`.
  * **Code Formatting & Linting (`format_code.py` / `format_code.bat`)**:
    * *Function*: Enforces clean code standards by automatically formatting all Python files with `black` and checking for stylistic PEP 8 issues with `flake8`.
    * *Usage*: Run `python scripts/format_code.py [target_path]` or run `format_code.bat` from Windows Explorer.

---

## Contact and Contributing

Contributions are welcome. Please open an issue to align on design decisions before submitting pull requests.

- **Developer**: Kamal Yaser
- **Email**: `kamalyaser31@gmail.com`
- **Telegram**: [kamalyaser31](https://t.me/kamalyaser31)
- **Issues Tracker**: [GitHub Issues](https://github.com/kamalyaser31/simple-player/issues)

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for the full license text.
