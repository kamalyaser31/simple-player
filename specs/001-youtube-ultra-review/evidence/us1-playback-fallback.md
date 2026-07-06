# US1 Evidence: Playback and Local Fallback

- Evidence ID: EVID-US1-026
- Type: source-inspection
- Result: risk

## Observations

- `player/youtube/flow.py:315-355` opens resolved YouTube streams through the player with YouTube source metadata.
- `player/youtube/flow.py:417-472` prefetches streams but does not queue them into the player.
- `player/core/player/lifecycle.py:20-27` advances only through already queued playlist state on EOF.
- `player/app_actions/file_actions.py:220-239` opens local file/folder after clearing YouTube session and does not require YouTube helpers.
- `player/app_actions/file_actions.py:246-269` opens generic streams without YouTube helper checks.
- `player/core/mpv_engine.py:62-68` enables MPV Windows media controls and media keys.
- `player/core/controller.py:232-236` also creates a custom Windows media bridge.
- `player/core/controller.py:432-453` shutdown omits explicit YouTube session/prefetch executor cleanup.

## Finding Support

- Supports YT-003, YT-005, and YT-016.

## Validation Needed

- Manual local playback after YouTube failure, natural EOF, SMTC/media-key behavior, and shutdown during background YouTube work.
