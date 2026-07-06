# US1 Evidence: Search

- Evidence ID: EVID-US1-020
- Type: source-inspection
- Result: risk

## Observations

- `player/youtube/flow.py:144-149` handles missing components in search with spoken feedback only.
- `player/youtube/flow.py:253-291` runs the search task, preloads first stream when available, and displays results.
- `player/youtube/search.py:22-35` uses `py_yt.VideosSearch` with settings-derived language and region.
- `player/youtube/search.py:63-74` runs async calls with a 20-second timeout wrapper.
- `player/youtube/search.py:98-110` converts results to `YtItem` with title, URL, channel, and duration metadata where available.

## Finding Support

- Supports YT-010 and YT-015.

## Validation Needed

- Manual search with missing helpers, no results, invalid locale settings, cancellation, and screen-reader feedback.
