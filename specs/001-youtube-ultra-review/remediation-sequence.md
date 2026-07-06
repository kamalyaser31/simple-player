# YouTube Ultra Review Remediation Sequence

## Story 3 Validation Checklists

Remediation ordering checklist:

- Release blockers are listed before important hardening.
- Important hardening is listed before future improvements.
- Critical/high playback, data-loss, accessibility, and blocking failure issues are not mixed with optional refactors.

Release-blocker mapping checklist:

- Each release-blocker recommendation maps to a high finding in `youtube-ultra-review.md`.
- Each release-blocker includes validation needed before closure.

Future-improvement classification checklist:

- Future improvements are not described as required release work.
- Future improvements are limited to low-risk cleanup, quality, or maintainability work.

## Release Blockers

### REC-001: Fix session ownership and targeted cleanup for YouTube results dialogs

- Maps to: YT-001.
- Priority: release-blocker.
- Action: Make `show_res()` session ownership explicit and ensure dialog close cancels only the displayed session or preserves an existing playback session when appropriate.
- Expected benefit: Prevents users from losing return-to-results or next-track state when exploring another search/playlist.
- Validation needed: Start one YouTube session, open and close another results dialog, then verify original session state, prefetch cancellation, Escape, and Next behavior.

### REC-002: Synchronize session queued state with source removal

- Maps to: YT-002.
- Priority: release-blocker.
- Action: Clear/rebuild `ses["queued"]` when `remove_sources()` removes YouTube-owned player sources, or verify actual player queue membership in `_ensure_queued()`.
- Expected benefit: Prevents stale queue state after returning to results.
- Validation needed: Play a result, press Escape, then press Next and verify a real queued stream exists.

### REC-003: Integrate YouTube next-track with natural EOF

- Maps to: YT-003.
- Priority: release-blocker.
- Action: Resolve/queue the next YouTube item before natural EOF or call YouTube next handling from the player finished-file path.
- Expected benefit: Keeps playlist/search playback continuous without requiring manual Next.
- Validation needed: Let multiple YouTube items play through naturally with and without prefetch completion.

### REC-004: Make Deno install/extraction atomic

- Maps to: YT-004.
- Priority: release-blocker.
- Action: Extract Deno to a temporary file, validate it, replace atomically, and remove partial targets on cancel/error.
- Expected benefit: Prevents broken helper binaries from passing availability checks.
- Validation needed: Interrupt extraction and verify missing-component detection or repair prompt works.

### REC-005: Choose one Windows media integration owner

- Maps to: YT-005.
- Priority: release-blocker.
- Action: Decide whether MPV or `WindowsMediaBridge` owns media controls; disable the other path for media keys/SMTC.
- Expected benefit: Avoids duplicate media sessions and media-key events.
- Validation needed: Verify local and YouTube playback with SMTC and hardware media keys on Windows.

## Important Hardening

### REC-006: Reject unsupported YouTube URLs before stream resolution

- Maps to: YT-006.
- Priority: important-hardening.
- Validation needed: Link parser tests and manual checks for homepage, channel, invalid watch, unsupported path, video, playlist, and mixed links.

### REC-007: Surface background failure feedback

- Maps to: YT-007.
- Priority: important-hardening.
- Validation needed: Network-disabled load-more, prefetch, and next-track checks confirm spoken/visible outcomes.

### REC-008: Add stream cache freshness handling

- Maps to: YT-008.
- Priority: important-hardening.
- Validation needed: Cached stream TTL/retry tests and manual replay after cache age exceeds TTL.

### REC-009: Harden subprocess timeouts and cancellation cleanup

- Maps to: YT-009.
- Priority: important-hardening.
- Validation needed: Simulated hung resolver/download verifies timeout, terminate, wait, and kill paths.

### REC-010: Make missing-component search failure visible

- Maps to: YT-010.
- Priority: important-hardening.
- Validation needed: Search with missing helpers shows visible and spoken guidance and local playback still works.

### REC-011: Respect focused controls in result dialogs

- Maps to: YT-011.
- Priority: important-hardening.
- Validation needed: Keyboard-only tab/Enter through list, Download, Play, and Close controls.

### REC-012: Improve cancellation and accessible progress feedback

- Maps to: YT-012, YT-013.
- Priority: important-hardening.
- Validation needed: Screen-reader and keyboard checks for search/load/download/install cancel and progress milestones.

### REC-013: Clarify or expand component update behavior

- Maps to: YT-014.
- Priority: important-hardening.
- Validation needed: Update checks for missing yt-dlp, stale yt-dlp, stale Deno, and all components already installed.

### REC-014: Validate settings-derived YouTube values

- Maps to: YT-015.
- Priority: important-hardening.
- Validation needed: Unit tests or manual config edits for prefetch count and search language/region.

### REC-015: Stop YouTube background work on shutdown

- Maps to: YT-016.
- Priority: important-hardening.
- Validation needed: App shutdown while prefetch, resolve, download, install, or update work is active.

## Future Improvements

### REC-016: Reuse strict host validation for current-source checks

- Maps to: YT-017.
- Priority: future-improvement.
- Validation needed: Unit tests for valid and invalid YouTube-like hosts.

### REC-017: Distinguish description failure from empty description

- Maps to: YT-018.
- Priority: future-improvement.
- Validation needed: Manual and automated checks for no-description video versus failed metadata lookup.

### REC-018: Improve result labels with channel/index metadata

- Maps to: YT-019.
- Priority: future-improvement.
- Validation needed: Screen-reader review of duplicate-title search results.

### REC-019: Consolidate duplicate task dialog implementations

- Maps to: maintenance observation in `evidence/us3-future-improvements.md`.
- Priority: future-improvement.
- Validation needed: Confirm all YouTube task paths use the shared accessible task dialog after consolidation.
