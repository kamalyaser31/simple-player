# US2 Evidence: Playlist and Mixed Link Journey

- Evidence ID: EVID-US2-035
- Type: source-inspection
- Result: risk

## Covered Behavior

- Mixed video-plus-playlist prompts: `player/youtube/ui_utils.py:54-94`.
- Link kind handling: `player/youtube/flow.py:73-127`.
- Playlist inspection: `player/youtube/flow.py:300-312` and resolver support.
- Results dialog display starts prefetch: `player/youtube/results.py:28-29`.

## Validation Status

- Coverage status: partial.
- Not run: live playlist, mixed URL, unavailable playlist item, close-dialog cleanup.
- Linked findings: YT-001, YT-007.
