# US1 Evidence: Link Validation and Resolution

- Evidence ID: EVID-US1-021
- Type: source-inspection
- Result: risk

## Observations

- `player/youtube/link_validator.py:37-52` validates HTTP(S) and YouTube host names.
- `player/youtube/link_validator.py:96-98` defaults unknown YouTube URLs to `video` kind.
- `player/youtube/flow.py:63-141` handles direct link validation, mixed links, playlist links, channels, and direct video playback.
- `player/youtube/resolver.py:130-166` resolves streams through JSON extraction and `-g` fallbacks.
- `player/youtube/resolver.py:281-319` polls resolver subprocesses without a non-user maximum timeout.
- `player/youtube/resolver.py:356-364` detects 429/rate-limit diagnostics.

## Finding Support

- Supports YT-006 and YT-009.

## Validation Needed

- Manual and automated checks for unsupported YouTube pages, invalid links, rate limits, and hung resolver process cleanup.
