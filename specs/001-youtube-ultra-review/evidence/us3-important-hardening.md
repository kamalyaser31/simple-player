# US3 Evidence: Important Hardening

- Evidence ID: EVID-US3-051
- Type: source-inspection
- Result: risk

## Hardening Recommendations

- REC-006: Reject unsupported YouTube URLs before stream resolution. Maps to YT-006.
- REC-007: Surface background failure feedback. Maps to YT-007.
- REC-008: Add stream cache freshness handling. Maps to YT-008.
- REC-009: Harden subprocess timeouts and cancellation cleanup. Maps to YT-009.
- REC-010: Make missing-component search failure visible. Maps to YT-010.
- REC-011: Respect focused controls in result dialogs. Maps to YT-011.
- REC-012: Improve cancellation and accessible progress feedback. Maps to YT-012 and YT-013.
- REC-013: Clarify or expand component update behavior. Maps to YT-014.
- REC-014: Validate settings-derived YouTube values. Maps to YT-015.
- REC-015: Stop YouTube background work on shutdown. Maps to YT-016.

## Validation Needed

- Mix of source-level tests for parsing/settings/state and manual checks for GUI, playback, screen reader, helper install/update, and Windows behavior.
