# Simple Audio Player

A feature-rich, accessible Windows desktop audio and media player built with Python and wxPython. Designed with keyboard accessibility and screen reader support in mind.

**Version:** 1.0.1  
**Author:** Kamal Yaser  
**Repository:** [GitHub](https://github.com/kamalyaser31/simple-player)

---

## Features

- **Wide Format Support:** Play all common audio and video files.
- **YouTube Integration:** Search, play, and download YouTube videos and playlists.
- **Advanced Audio Processing:** Includes silence removal, audio normalization, and mono conversion.
- **Full Keyboard Accessibility:** Control everything with your keyboard.
- **Screen Reader Support:** Works with JAWS, NVDA, and other screen readers.
- **Customizable:** Change keyboard shortcuts, language (English/Arabic), and other settings.

---

## System Requirements

- **Operating System:** Windows 7 SP1 or later (Windows 10+ recommended)
- **RAM:** Minimum 256 MB
- **Disk Space:** 200 MB for installation
- **Audio Device:** A working audio output device

---

## Supported Formats

- **Audio:** AAC, AIFF, ALAC, FLAC, M4A, MP3, OGG, OPUS, WAV, WMA
- **Video:** 3GP, AVI, FLV, M2TS, M4V, MKV, MOV, MPEG, MP4, MPG, TS, WebM, WMV

---

## Installation

### Windows Installer (Recommended)

1. Download the latest `SimpleAudioPlayerSetup.exe` from the [Releases page](https://github.com/kamalyaser31/simple-player/releases).
2. Run the installer and follow the on-screen instructions.

### Portable Version

1. Download the portable ZIP file from the [Releases page](https://github.com/kamalyaser31/simple-player/releases).
2. Extract the ZIP file to any folder.
3. Run `SimpleAudioPlayer.exe`.

---

## Usage

For detailed instructions, please refer to the [Full User Guide](player/docs/en/userguide.html).

### Basic Playback

- **Open a file:** Go to `File > Open File` or press `Ctrl+O`.
- **Play/Pause:** Press `Space`.
- **Navigate:** Use the `Right` and `Left` arrow keys to seek.
- **Volume:** Use the `Up` and `Down` arrow keys to adjust the volume.

---

## Development

If you want to contribute to the project, you can build it from source.

### Project Structure

```
simple-player/
├── player/                    # Main application directory
│   ├── app.py                # Application entry point
│   ├── SimpleAudioPlayer.py   # GUI entry point
│   ├── requirements.txt       # Python dependencies
│   ├── SimpleAudioPlayer.spec # PyInstaller configuration
│   ├── simple_audio_player.iss # Inno Setup configuration
│   │
│   ├── core/                 # Core functionality
│   │   ├── controller.py     # Main application controller
│   │   ├── mpv_engine.py     # Media playback engine
│   │   ├── keyboard_handler.py # Global keyboard input
│   │   ├── media_library.py  # File scanning/indexing
│   │   └── player/           # Player implementation
│   │
│   ├── config/               # Configuration management
│   │   ├── constants.py      # Application constants
│   │   ├── settings_manager.py # Settings persistence
│   │   ├── shortcuts.py      # Keyboard shortcuts
│   │   ├── localization.py   # i18n support
│   │   └── file_associations.py # Windows file registration
│   │
│   ├── ui/                   # User interface
│   │   ├── main_frame.py     # Main window
│   │   ├── mainwin/          # Main window components
│   │   ├── dialogs.py        # UI dialogs
│   │   ├── settings_dialog.py # Settings window
│   │   └── prefs/            # Settings panels
│   │
│   ├── app_actions/          # Application actions
│   │   ├── playback_actions.py # Playback control
│   │   ├── file_actions.py   # File operations
│   │   ├── device_actions.py # Audio device management
│   │   └── help_actions.py   # Help/documentation
│   │
│   ├── youtube/              # YouTube integration
│   │   ├── search.py         # Search functionality
│   │   ├── download.py       # Download functionality
│   │   ├── flow.py           # YouTube workflow
│   │   └── components.py     # Component management
│   │
│   ├── playlist/             # Playlist management
│   │   ├── state.py          # Playlist state
│   │   └── state/            # Playlist state modules
│   │
│   ├── helpers/              # Utility functions
│   │   ├── utils.py          # Common utilities
│   │   ├── file_helpers.py   # File operations
│   │   └── clipboard_utils.py # Clipboard handling
│   │
│   ├── locale/               # Localization files
│   │   └── ar/, en/          # Language directories
│   │
│   ├── docs/                 # Documentation
│   │   └── en/, ar/          # Language docs
│   │
│   └── sounds/               # Audio resources
│       └── speaker_test.wav  # Test sound file
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `wxPython` | GUI framework |
| `python-libmpv` | Media playback |
| `pynput` | Global keyboard handling |
| `appGuard` | Single instance enforcement |
| `accessible_output3` | Screen reader integration |
| `py-yt-search` | YouTube search |
| `winsdk` | Windows SDK integration |

### Building from Source

#### Prerequisites
- Python 3.7 or higher
- Git

#### Steps

1. **Clone the Repository**
   ```powershell
   git clone https://github.com/kamalyaser31/simple-player.git
   cd simple-player/player
   ```

2. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```powershell
   python SimpleAudioPlayer.py
   ```
---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Support

If you need help, have suggestions, or want to report a bug, please use one of the following channels:

- **Report Issues:** [GitHub Issues](https://github.com/kamalyaser31/simple-player/issues)
- **Email Support:** kamalyaser31@gmail.com
- **Telegram:** [@kamalyaser31](https://t.me/kamalyaser31)

---

## Frequently Asked Questions

**Q: Is Simple Audio Player free?**  
A: Yes, it is free and open-source.

**Q: Can I use it on Mac or Linux?**  
A: Currently, it is Windows-only.

**Q: Can I customize keyboard shortcuts?**  
A: Yes, you can customize all shortcuts in `Settings > Keyboard Shortcuts`.
