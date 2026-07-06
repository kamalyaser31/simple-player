# US2 Evidence: Download Journey

- Evidence ID: EVID-US2-039
- Type: source-inspection
- Result: risk

## Covered Behavior

- Current video download path: `player/youtube/video.py:50-73`.
- Destination prompt: `player/youtube/ui_utils.py:127-138`.
- Progress text: `player/youtube/ui_utils.py:141-152`.
- Download worker: `player/youtube/download.py:15-67`.
- Cancellation stop: `player/youtube/download.py:121-125`.

## Validation Status

- Coverage status: partial.
- Not run: real download, cancellation, failed output path, hung subprocess, screen-reader progress.
- Linked findings: YT-009, YT-012, YT-013.
