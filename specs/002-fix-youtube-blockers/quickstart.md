# Quickstart: Fix YouTube Release Blockers Validation

## Prerequisites

- Windows development environment capable of running the application from source.
- Project dependencies installed according to `README.md`.
- A local media file available for fallback playback validation.
- YouTube helper components available for normal-flow checks and removable or interruptible
  for failure-path checks.
- Network access for live YouTube search/link playback unless testing failure recovery.
- Screen reader available for accessibility feedback checks when possible.

## Validate Planning Artifacts

1. Confirm the feature spec exists at `specs/002-fix-youtube-blockers/spec.md`.
2. Confirm this plan exists at `specs/002-fix-youtube-blockers/plan.md`.
3. Confirm research decisions exist at `specs/002-fix-youtube-blockers/research.md`.
4. Confirm the data model exists at `specs/002-fix-youtube-blockers/data-model.md`.
5. Confirm contracts exist under `specs/002-fix-youtube-blockers/contracts/`.

Expected outcome: artifacts describe fixes for YT-001 through YT-005 only.

## Validate YouTube Session Continuity

1. Run the application from `player/` following `README.md`.
2. Start a YouTube search or playlist with at least three playable items.
3. Play the first item.
4. Open a second YouTube results view and close it without starting playback from it.
5. Return to the original results and use explicit Next.
6. Let the next item finish naturally and observe whether playback advances.

Expected outcome: original session state remains intact, queued state is accurate, and
natural end-of-item playback advances or gives clear feedback if the next item cannot play.

## Validate Helper Component Integrity

1. Test normal helper readiness with valid helper components present.
2. Interrupt helper setup during download, extraction, or replacement where practical.
3. Restart the application.
4. Attempt a YouTube action that requires helpers.
5. Play a local file after the helper failure.

Expected outcome: partial or unusable helpers are not reported as ready, recovery guidance
is visible or spoken, and local playback remains usable.

## Validate Windows Media Control Ownership

1. Play a local file.
2. Use Windows media controls or hardware media keys for Play/Pause, Next, and Previous.
3. Verify each command produces exactly one playback action.
4. Repeat with YouTube playback.
5. Verify Windows media status shows one coherent current item and no duplicate sessions.
6. Disable or simulate unavailable Windows media integration if practical and repeat local
   keyboard playback controls.

Expected outcome: one effective owner handles Windows media commands and status; fallback
keeps local playback and keyboard controls usable.

## Completion Evidence

Before the feature is considered complete, record validation evidence for:

- YT-001: session ownership and targeted cleanup.
- YT-002: queued-state synchronization after return-to-results.
- YT-003: natural end-of-item YouTube advancement.
- YT-004: helper integrity after interrupted setup.
- YT-005: single Windows media-control ownership.
