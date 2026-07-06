# US2 Evidence: Local Playback Fallback

- Evidence ID: EVID-US2-043
- Type: source-inspection
- Result: risk

## Covered Behavior

- Local open file/folder path: `player/app_actions/file_actions.py:220-239`.
- Generic stream open path: `player/app_actions/file_actions.py:246-269`.
- YouTube helper checks block only YouTube flows: `player/youtube/flow.py:43-61`, `player/youtube/flow.py:144-149`.
- Windows media bridge guards missing `winsdk`: `player/core/windows_media.py:13-24`.
- Controller shutdown closes custom Windows bridge and MPV: `player/core/controller.py:432-453`.

## Validation Status

- Coverage status: partial.
- Not run: local playback after missing helpers, failed install, failed stream resolve, active YouTube session, and Windows media failures.
- Linked findings: YT-005, YT-016.
