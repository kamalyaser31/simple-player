# US1 Evidence: Downloads

- Evidence ID: EVID-US1-023
- Type: source-inspection
- Result: risk

## Observations

- `player/youtube/download.py:15-35` builds a list-form `yt-dlp` command for M4A extraction.
- `player/youtube/download.py:53-67` reads progress from stdout lines and checks cancellation after line reads.
- `player/youtube/download.py:80-94` parses percentage progress and forwards it to task UI.
- `player/youtube/download.py:121-125` terminates the process on cancellation but does not wait/kill escalate.

## Finding Support

- Supports YT-009 and YT-012.

## Validation Needed

- Manual download success, failure, output folder, cancellation, and simulated hung process checks.
