# US1 Evidence: Helper Components

- Evidence ID: EVID-US1-024
- Type: source-inspection
- Result: risk

## Observations

- `player/youtube/components.py:56-65` checks helper availability by file existence only.
- `player/youtube/components.py:260-317` downloads yt-dlp through a temporary file and atomic replace pattern.
- `player/youtube/components.py:320-344` extracts Deno by writing directly to `deno.exe`.
- `player/youtube/components.py:165-178` updates only existing yt-dlp.
- `player/update/actions.py:34-80` labels the workflow as updating YouTube components but delegates to yt-dlp update.

## Finding Support

- Supports YT-004 and YT-014.

## Validation Needed

- Manual interrupted Deno extraction, missing yt-dlp update, stale Deno update, and install repair checks.
