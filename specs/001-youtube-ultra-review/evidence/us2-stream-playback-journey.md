# US2 Evidence: Stream Playback Journey

- Evidence ID: EVID-US2-037
- Type: source-inspection
- Result: risk

## Covered Behavior

- Prep/play flow: `player/youtube/flow.py:315-414`.
- Stream resolve fallback sequence: `player/youtube/resolver.py:74-113`, `player/youtube/resolver.py:130-166`.
- Stream metadata handoff: `player/core/player/load.py:30-48`.
- Cache reuse: `player/youtube/flow.py:582-604`.

## Validation Status

- Coverage status: partial.
- Not run: MPV playback start, stale signed stream URL, rate-limit recovery, local playback after stream failure.
- Linked findings: YT-008, YT-009.
