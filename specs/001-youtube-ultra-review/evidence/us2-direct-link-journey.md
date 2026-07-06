# US2 Evidence: Direct Link Journey

- Evidence ID: EVID-US2-034
- Type: source-inspection
- Result: risk

## Covered Behavior

- Open path: File > Open YouTube Link, Ctrl+Shift+Y.
- Prompt: `player/youtube/ui_utils.py:26-37`.
- HTTP and host validation: `player/youtube/link_validator.py:37-52`.
- Unknown YouTube page defaulting: `player/youtube/link_validator.py:96-98`.
- Direct playback path: `player/youtube/flow.py:129-141`.
- Resolver subprocess path: `player/youtube/resolver.py:130-166`, `player/youtube/resolver.py:281-319`.

## Validation Status

- Coverage status: partial.
- Not run: live valid, invalid, unsupported, removed, unavailable, and rate-limited link checks.
- Linked findings: YT-006, YT-009.
