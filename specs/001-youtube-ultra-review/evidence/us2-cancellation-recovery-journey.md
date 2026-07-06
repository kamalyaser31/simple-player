# US2 Evidence: Cancellation and Failure Recovery Journey

- Evidence ID: EVID-US2-041
- Type: source-inspection
- Result: risk

## Covered Behavior

- Task cancel path: `player/youtube/task_ui.py:48-57`.
- Worker shutdown on cancel: `player/youtube/task_ui.py:117-120`.
- Search cancel return: `player/youtube/flow.py:285-286`.
- Stream load cancel return: `player/youtube/flow.py:406-407`.
- Download cancel return: `player/youtube/video.py:67-68`.
- Silent background errors: `player/youtube/flow.py:447-456`, `player/youtube/flow.py:492-512`, `player/youtube/results.py:159-163`.

## Validation Status

- Coverage status: partial.
- Not run: cancel while search, stream load, download, update, and prefetch are active.
- Linked findings: YT-007, YT-009, YT-012, YT-016.
