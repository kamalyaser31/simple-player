# US2 Evidence: Search Journey

- Evidence ID: EVID-US2-033
- Type: source-inspection
- Result: risk

## Covered Behavior

- Search entry path: File > Search YouTube, Ctrl+Y.
- Prompt: `player/youtube/ui_utils.py:40-51`.
- Missing components: `player/youtube/flow.py:144-149` speaks only.
- Search task: `player/youtube/flow.py:253-291`.
- Search adapter and result conversion: `player/youtube/search.py:22-35`, `player/youtube/search.py:98-110`.
- Load-more trigger: `player/youtube/results.py:122-175`.

## Validation Status

- Coverage status: partial.
- Not run: live network search, no-results response, cancellation, screen-reader feedback.
- Linked findings: YT-007, YT-010, YT-012, YT-015.
