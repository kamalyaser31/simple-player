# Manual Validation Environment

- Evidence ID: EVID-FOUNDATION-014
- Type: documentation-reference
- Result: not-run

## Assumptions

- Windows development environment can run the application from `player/`.
- Project dependencies follow `README.md`.
- `yt-dlp.exe` and `deno.exe` can be present, absent, stale, blocked, or intentionally interrupted for failure-path checks.
- Network access is available for live YouTube validation unless testing offline recovery.
- Screen-reader checks are required for spoken feedback, dialog labels, progress status, and keyboard-only flows.

## Limitations

- This implementation pass performed current-source inspection and artifact validation only.
- Live MPV playback, helper downloads, SMTC/media-key behavior, and screen-reader announcements remain manual validation items.
