# Contract: Helper Component Integrity

## Scope

This contract covers release blocker YT-004 for YouTube helper component setup,
readiness, and recovery.

## Required Behaviors

1. Helper setup must never leave a partial or unusable helper file reported as ready.
2. Helper replacement must preserve either the previous usable helper or a clean non-ready
   state when installation, extraction, update, or cancellation fails.
3. Readiness checks must distinguish missing, ready, broken, and repair-required states.
4. Starting a YouTube action with a missing or broken helper must provide clear visible or
   spoken recovery guidance.
5. Missing, broken, installing, or repair-required helpers must not prevent local media
   playback.

## Acceptance Checks

- Interrupt helper setup during download, extraction, and replacement where practical.
- Restart the application and verify partial helpers are not reported as ready.
- Start a YouTube action with missing or broken helpers and verify recovery guidance.
- Play a local file after helper failure and verify playback remains usable.

## Evidence Required

- Validation record for interrupted setup.
- Validation record for readiness classification.
- Validation record for local playback fallback after helper failure.
