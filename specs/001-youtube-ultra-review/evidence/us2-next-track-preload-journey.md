# US2 Evidence: Next-Track and Preload Journey

- Evidence ID: EVID-US2-038
- Type: source-inspection
- Result: risk

## Covered Behavior

- Custom next path: `player/youtube/flow.py:212-237`.
- Pending next resolution: `player/youtube/flow.py:475-516`.
- Prefetch: `player/youtube/flow.py:417-472`.
- Queue ensure: `player/youtube/flow.py:542-570`.
- Generic EOF: `player/core/player/lifecycle.py:20-27`.

## Validation Status

- Coverage status: partial.
- Not run: explicit Next before/after prefetch, failed preload, unavailable next item, natural EOF.
- Linked findings: YT-002, YT-003, YT-007.
