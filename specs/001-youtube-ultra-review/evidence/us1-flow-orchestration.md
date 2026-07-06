# US1 Evidence: Flow Orchestration

- Evidence ID: EVID-US1-019
- Type: source-inspection
- Result: risk

## Observations

- `player/youtube/flow.py:144-183` runs search and displays results.
- `player/youtube/flow.py:117-127` displays playlist results.
- `player/youtube/flow.py:195-198` handles Escape by removing session sources but does not clear session queued state.
- `player/youtube/flow.py:428-472` starts prefetch jobs in a module-level executor.
- `player/youtube/flow.py:492-512` resolves a pending next item and silently returns on non-dict results.
- `player/youtube/flow.py:558-571` trusts the session queued set when deciding whether a URL is already queued.
- `player/youtube/flow.py:582-604` caches resolved streams by URL/options without expiry validation.

## Finding Support

- Supports YT-002, YT-007, and YT-008.

## Validation Needed

- Manual checks for Escape, Next after Escape, background next failure, prefetch failure, and stale cached streams.
