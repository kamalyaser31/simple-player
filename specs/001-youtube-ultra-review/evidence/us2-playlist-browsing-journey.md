# US2 Evidence: Playlist Browsing and Return to Results Journey

- Evidence ID: EVID-US2-036
- Type: source-inspection
- Result: risk

## Covered Behavior

- Dialog controls and context menu: `player/ui/yt_dialogs.py:152-185`.
- Accelerators and Enter handling: `player/ui/yt_dialogs.py:238-268`.
- Result play, download, copy, browser, channel actions: `player/youtube/results.py:35-100`.
- Dialog close cleanup: `player/youtube/results.py:112-113`.
- Escape return path: `player/youtube/flow.py:190-209`.

## Validation Status

- Coverage status: partial.
- Not run: keyboard-only tab order, screen-reader labels, return-to-results after playback, multiple active result dialogs.
- Linked findings: YT-001, YT-011, YT-019.
