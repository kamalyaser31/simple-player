# US1 Evidence: Action Entrypoints

- Evidence ID: EVID-US1-018
- Type: source-inspection
- Result: risk

## Observations

- `player/youtube/actions.py:1-15` is a facade that re-exports flow and current-video actions.
- `player/actions.py:166-194` defines user-facing YouTube action IDs and shortcuts.
- `player/core/controller.py:267-272` dispatches actions to open link, search, description, download, and copy current video link.
- `player/youtube/video.py:24-36` and `player/youtube/video.py:76-90` load current video details for description.
- `player/youtube/video.py:105-111` treats empty or failed description loading as no description.

## Finding Support

- Supports YT-018: description lookup failure is indistinguishable from a genuinely empty description.

## Validation Needed

- Manual check for current-video description with network failure and with a video that has no description.
