# US2 Evidence: Helper Component Journey

- Evidence ID: EVID-US2-040
- Type: source-inspection
- Result: risk

## Covered Behavior

- Startup prompt: `player/youtube/startup.py:17-38`.
- Manual install: `player/youtube/startup.py:40-64`.
- Install missing helpers: `player/youtube/components.py:142-162`.
- Deno extraction: `player/youtube/components.py:320-344`.
- Update action: `player/update/actions.py:34-80`.

## Validation Status

- Coverage status: partial.
- Not run: missing, outdated, blocked, interrupted install, stale Deno, update-before-install.
- Linked findings: YT-004, YT-010, YT-014.
