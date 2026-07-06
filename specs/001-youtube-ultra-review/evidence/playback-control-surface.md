# Playback and Control Surface

- Evidence ID: EVID-FOUNDATION-011
- Type: source-inspection
- Result: risk

## Current Surface

- `player/core/controller.py:232-236` owns a custom `WindowsMediaBridge`.
- `player/core/controller.py:432-453` shuts down global keyboard, timers, recording, settings, Windows media bridge, and MPV, but does not explicitly clear YouTube session state.
- `player/core/action_context.py` provides the action context used by YouTube flow modules.
- `player/core/player/load.py:30-48` opens stream URLs and records `source_url` metadata.
- `player/core/player/lifecycle.py:20-27` advances only through already queued playlist state on EOF.
- `player/core/mpv_engine.py:62-68` enables MPV Windows media controls and input media keys on Windows.
- `player/core/windows_media.py:13-24` guards `winsdk` imports and safely disables the custom bridge when unavailable.

## Risks

- EOF handling does not call YouTube-specific next-track resolution.
- Shutdown does not cancel YouTube prefetch/resolve state.
- MPV and the custom bridge may both own Windows media integration.
