# US1 Evidence: Results and Session State

- Evidence ID: EVID-US1-022
- Type: source-inspection
- Result: risk

## Observations

- `player/youtube/results.py:28-29` starts prefetch when showing results.
- `player/youtube/results.py:112-113` clears the context session when the dialog closes.
- `player/youtube/state.py:8-24` creates sessions with items, queued URLs, jobs, pending-next state, cancel flag, and prefetch metadata.
- `player/youtube/state.py:45-70` clears the current context session and cancels known futures.
- `player/youtube/state.py:95-103` detects YouTube sources with substring host matching.
- New result sessions can be shown before being installed as the current context session.

## Finding Support

- Supports YT-001 and YT-017.

## Validation Needed

- Manual checks for opening a second result dialog while one YouTube session is active and for invalid YouTube-like host metadata.
