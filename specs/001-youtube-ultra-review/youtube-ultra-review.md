# YouTube Ultra Review

## Executive Summary

Overall readiness assessment: not release-ready for a YouTube-focused release without targeted hardening. Core workflows exist and are mostly separated from the UI, but current-source inspection found high-risk issues in session cleanup, next-track continuity, helper component integrity, and Windows media integration ownership. Manual GUI, playback, screen-reader, and Windows validation still need to be run before closing any finding.

Finding counts by severity:

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 5 |
| Medium | 9 |
| Low | 5 |
| Info | 0 |

Release-blocker summary:

- YT-001: Closing a newly opened YouTube results dialog can clear the previous active session and leave new prefetch work uncancelled.
- YT-002: Escape removes YouTube player sources but leaves session queued state stale.
- YT-003: Natural end-of-file playback does not integrate with YouTube next-track resolution.
- YT-004: Deno extraction writes directly to `deno.exe`, so interrupted extraction can leave a partial executable that still passes availability checks.
- YT-005: MPV Windows media controls and the custom `WindowsMediaBridge` can both own media-key/SMTC integration.

Review authority:

- Evidence is based on current source, current feature documents, and explicitly marked manual validation gaps.
- Stale historical plans are not used as standalone evidence.

Acceptance checklist:

- Findings include ID, severity, category, affected journey, impact, evidence, verification guidance, recommended next action, and release-blocker status.
- Critical/high findings include reproduction or verification guidance.
- User-facing failure findings describe expected recovery.
- Accessibility findings describe keyboard path or spoken/visible feedback impact.
- Platform/helper findings describe whether local playback remains usable.

## Journey Coverage Matrix

See `specs/001-youtube-ultra-review/validation-matrix.md` for the complete matrix.

Summary:

| Journey | Coverage Status | Key Result |
|---------|-----------------|------------|
| Search | Partial | Source inspected; manual keyboard/search/network validation not run. |
| Direct link opening | Partial | Source inspected; unsupported URL classification risk found. |
| Playlist browsing | Partial | Source inspected; session cleanup and results keyboard risks found. |
| Stream playback | Partial | Source inspected; stream cache and timeout risks found. |
| Next-track behavior | Partial | Source inspected; stale queued state and EOF continuity risks found. |
| Downloads | Partial | Source inspected; cancellation and timeout risks found. |
| Component setup/update | Partial | Source inspected; Deno integrity and update-label risks found. |
| Cancellation and failure recovery | Partial | Source inspected; several silent/delayed cancellation outcomes found. |
| Accessibility feedback | Partial | Source inspected; spoken-only/silent feedback risks found. |
| Local playback fallback | Partial | Source inspected; local playback is mostly isolated but needs manual confirmation. |

## Findings

### YT-001: Results dialog cleanup can clear the wrong YouTube session

- Severity: High
- Category: risk
- Affected journey: playlist browsing, search results, cancellation and failure recovery
- Impact: A user can lose return-to-results or next-track state for the currently playing YouTube session by opening and closing another search or playlist dialog. The new dialog can also start prefetch work that is not cancelled when it closes.
- Evidence: `specs/001-youtube-ultra-review/evidence/us1-results-state.md`; current source `player/youtube/flow.py:117-127`, `player/youtube/flow.py:160-183`, `player/youtube/results.py:28-29`, `player/youtube/results.py:112-113`, `player/youtube/state.py:45-49`, `player/youtube/flow.py:428-472`.
- Reproduction or verification guidance: Start playback from one YouTube result set, open another search or playlist result dialog, close it without playing, then press Escape or Next in the original session and inspect whether the original session state and new prefetch jobs remain correct.
- Recommended next action: Make result dialog session ownership explicit. Either install the displayed session before prefetch and close handling, or pass the displayed session to targeted cleanup that cancels only that session.
- Release-blocker status: Yes.

### YT-002: Escape removes player sources but leaves YouTube queued state stale

- Severity: High
- Category: risk
- Affected journey: playlist browsing, next-track behavior
- Impact: After returning from YouTube playback to results, the player queue can be purged while the session still believes URLs are queued. Subsequent next-track behavior can fail or skip required queueing.
- Evidence: `specs/001-youtube-ultra-review/evidence/us1-flow-orchestration.md`; current source `player/youtube/flow.py:195-198`, `player/youtube/flow.py:558-571`, `player/youtube/flow.py:574-579`.
- Reproduction or verification guidance: Play a YouTube playlist/search item, press Escape to return to results, then attempt Next and verify whether the next stream is queued in the player rather than only marked in session state.
- Recommended next action: Clear or rebuild `ses["queued"]` whenever session-owned sources are removed, or make `_ensure_queued()` verify actual player queue/source metadata.
- Release-blocker status: Yes.

### YT-003: Natural end-of-file does not advance through unresolved YouTube next items

- Severity: High
- Category: risk
- Affected journey: stream playback, next-track behavior
- Impact: A YouTube playlist/search session can stop at end of file unless the next stream was explicitly queued through the custom Next path. This weakens daily playlist playback reliability.
- Evidence: `specs/001-youtube-ultra-review/evidence/us1-playback-fallback.md`; current source `player/youtube/flow.py:333-354`, `player/youtube/flow.py:417-472`, `player/youtube/flow.py:542-570`, `player/core/player/lifecycle.py:20-27`.
- Reproduction or verification guidance: Play a YouTube playlist/search result with more than one item, do not press Next, let playback naturally finish, and verify whether the next item resolves and starts.
- Recommended next action: Integrate YouTube next resolution into the player end-of-file path or ensure the next YouTube stream is queued before natural EOF.
- Release-blocker status: Yes.

### YT-004: Interrupted Deno extraction can leave a partial executable that passes availability checks

- Severity: High
- Category: confirmed-defect risk
- Affected journey: component setup/update
- Impact: An interrupted extraction can leave `deno.exe` partially written. Availability checks use file existence only, so future YouTube flows may treat a broken helper as installed.
- Evidence: `specs/001-youtube-ultra-review/evidence/us1-helper-components.md`; current source `player/youtube/components.py:60-65`, `player/youtube/components.py:320-344`.
- Reproduction or verification guidance: Interrupt component installation during Deno extraction, confirm whether `player/deno.exe` remains, then run the missing-component check and a YouTube flow.
- Recommended next action: Extract Deno to a temporary file, verify it, then atomically replace `deno.exe`; remove partial targets on cancel or extraction error.
- Release-blocker status: Yes.

### YT-005: MPV media controls and custom WindowsMediaBridge can both own media-key integration

- Severity: High
- Category: risk
- Affected journey: Windows integration, local playback fallback
- Impact: Windows can receive duplicated or conflicting media sessions and media-key handling because MPV media controls are enabled while a custom SMTC bridge is also active.
- Evidence: `specs/001-youtube-ultra-review/evidence/us1-playback-fallback.md`; current source `player/core/mpv_engine.py:62-68`, `player/core/controller.py:232-236`, `player/core/windows_media.py:27-67`.
- Reproduction or verification guidance: On Windows, play local and YouTube media, inspect SMTC display/session behavior, and use hardware media keys to verify whether actions are duplicated or inconsistent.
- Recommended next action: Choose one integration owner. If the custom bridge is authoritative, disable MPV `media-controls` and `input-media-keys`.
- Release-blocker status: Yes.

### YT-006: Unsupported YouTube pages can be classified as playable videos

- Severity: Medium
- Category: confirmed-defect risk
- Affected journey: direct link opening
- Impact: YouTube homepage or other non-video pages can be sent to `yt-dlp` as videos, producing confusing late failures instead of immediate validation feedback.
- Evidence: `specs/001-youtube-ultra-review/evidence/us1-link-resolution.md`; current source `player/youtube/link_validator.py:96-98`, `player/youtube/flow.py:129-141`.
- Reproduction or verification guidance: Open `https://www.youtube.com/` or another unsupported YouTube page through Open YouTube Link and verify whether it is rejected before stream resolution.
- Recommended next action: Require `has_video` for direct-video playback unless the URL is a supported playlist type.
- Release-blocker status: No.

### YT-007: Background next, prefetch, and load-more failures are silent

- Severity: Medium
- Category: risk
- Affected journey: next-track behavior, playlist browsing, failure recovery
- Impact: Users can hear or see loading start, then receive no outcome when background work fails.
- Evidence: `specs/001-youtube-ultra-review/evidence/us1-flow-orchestration.md`, `specs/001-youtube-ultra-review/evidence/us2-cancellation-recovery-journey.md`; current source `player/youtube/flow.py:447-456`, `player/youtube/flow.py:492-512`, `player/youtube/results.py:159-163`.
- Reproduction or verification guidance: Trigger load-more or next-track with network disabled or unavailable video and verify whether any spoken or visible failure is provided.
- Recommended next action: Surface concise spoken/status feedback for failed background operations and clear any pending state.
- Release-blocker status: No.

### YT-008: Resolved stream cache has no expiry validation

- Severity: Medium
- Category: risk
- Affected journey: stream playback, next-track behavior
- Impact: Time-limited YouTube media URLs can be reused after expiry, causing playback failure that re-resolution could avoid.
- Evidence: `specs/001-youtube-ultra-review/evidence/us1-flow-orchestration.md`; current source `player/youtube/flow.py:582-604`, `player/youtube/flow.py:358-414`.
- Reproduction or verification guidance: Resolve a stream, wait beyond typical signed URL validity, then replay from cached resolution and compare with fresh resolution.
- Recommended next action: Store cache age/expiry and re-resolve after a short TTL or after player open failure.
- Release-blocker status: No.

### YT-009: Resolver and download subprocesses lack non-user timeout and kill escalation

- Severity: Medium
- Category: risk
- Affected journey: stream playback, downloads, cancellation and failure recovery
- Impact: A hung `yt-dlp` process can keep a task dialog open indefinitely unless the user cancels; termination may leave child work running.
- Evidence: `specs/001-youtube-ultra-review/evidence/us1-downloads.md`, `specs/001-youtube-ultra-review/evidence/us1-link-resolution.md`; current source `player/youtube/resolver.py:281-319`, `player/youtube/download.py:53-67`, `player/youtube/download.py:121-125`.
- Reproduction or verification guidance: Simulate a nonresponsive `yt-dlp` command or blocked network, then verify task timeout behavior and process cleanup after cancellation.
- Recommended next action: Add bounded operation timeouts and terminate, wait, kill cleanup for subprocess cancellation/failure.
- Release-blocker status: No.

### YT-010: Search missing-components failure is spoken-only

- Severity: Medium
- Category: risk
- Affected journey: search, accessibility feedback, component setup/update
- Impact: Sighted users may see no visible error, and screen-reader users receive only ephemeral feedback without an install path.
- Evidence: `specs/001-youtube-ultra-review/evidence/us1-accessibility-feedback.md`; current source `player/youtube/flow.py:144-149`, contrasting open-link `player/youtube/flow.py:43-48`, `player/youtube/flow.py:622-630`.
- Reproduction or verification guidance: Remove or rename helper binaries, invoke Search YouTube, and verify whether visible and spoken feedback both explain the problem and recovery path.
- Recommended next action: Reuse the visible error/install prompt path for search, while preserving spoken feedback.
- Release-blocker status: No.

### YT-011: Results dialog Enter shortcut can override focused button activation

- Severity: Medium
- Category: risk
- Affected journey: playlist browsing, accessibility feedback
- Impact: Keyboard and screen-reader users can tab to Download or Close, press Enter, and unexpectedly start playback because the dialog-level handler posts Play for any Enter key.
- Evidence: `specs/001-youtube-ultra-review/evidence/us1-accessibility-feedback.md`; current source `player/ui/yt_dialogs.py:161-163`, `player/ui/yt_dialogs.py:262-267`.
- Reproduction or verification guidance: Open results, tab focus to Download or Close, press Enter, and verify which action fires.
- Recommended next action: Restrict Enter-to-play to the results list focus and let buttons handle Enter normally.
- Release-blocker status: No.

### YT-012: Task dialogs dismiss immediately on cancel while work may continue silently

- Severity: Medium
- Category: risk
- Affected journey: cancellation and failure recovery, downloads, stream playback, component setup/update
- Impact: The user receives no reliable cancellation confirmation, and network/subprocess work can continue winding down after the dialog disappears.
- Evidence: `specs/001-youtube-ultra-review/evidence/us2-cancellation-recovery-journey.md`; current source `player/youtube/task_ui.py:48-57`, `player/youtube/task_ui.py:117-120`, `player/youtube/flow.py:285-286`, `player/youtube/flow.py:406-407`, `player/youtube/video.py:67-68`.
- Reproduction or verification guidance: Cancel search, loading stream, download, and description tasks; verify spoken/visible cancellation outcome and whether worker/subprocesses stop promptly.
- Recommended next action: Announce cancellation, show Canceling state where appropriate, and only dismiss immediately when safe or when cancel-request feedback is provided.
- Release-blocker status: No.

### YT-013: Progress/status dialogs lack accessible progress details

- Severity: Medium
- Category: missing-validation
- Affected journey: accessibility feedback, downloads, component setup/update
- Impact: Screen-reader users may not receive meaningful progress or status changes without manually reviewing controls.
- Evidence: `specs/001-youtube-ultra-review/evidence/us2-accessibility-journey.md`; current source `player/ui/task_dialogs.py:12-18`, `player/ui/task_dialogs.py:76-78`, `player/youtube/task_ui.py:64-77`, `player/youtube/ui_utils.py:141-152`.
- Reproduction or verification guidance: Run component install/download with a screen reader and verify whether status text and progress are announced at useful intervals.
- Recommended next action: Add accessible names/descriptions for status/log/gauge controls and announce coarse progress milestones.
- Release-blocker status: No.

### YT-014: Update YouTube components only updates yt-dlp

- Severity: Medium
- Category: risk
- Affected journey: component setup/update
- Impact: The menu label promises YouTube component update, but Deno is never updated and missing yt-dlp turns update into failure rather than install/repair.
- Evidence: `specs/001-youtube-ultra-review/evidence/us1-helper-components.md`; current source `player/ui/mainwin/menu.py:506-509`, `player/update/actions.py:34-80`, `player/youtube/components.py:165-178`.
- Reproduction or verification guidance: Use Help > Updates > Update YouTube components when Deno is stale or yt-dlp is missing and verify outcome.
- Recommended next action: Rename to Update yt-dlp or implement full component repair/update, including Deno and missing-component cases.
- Release-blocker status: No.

### YT-015: Settings-derived YouTube values can bypass UI constraints

- Severity: Medium
- Category: risk
- Affected journey: search, next-track behavior, component setup/update
- Impact: Manual config edits can create invalid search language/region values or excessive prefetch scheduling outside the UI SpinCtrl bounds.
- Evidence: `specs/001-youtube-ultra-review/evidence/helper-settings-surface.md`; current source `player/config/settings_manager.py:365-400`, `player/ui/prefs/youtube.py:46-48`, `player/youtube/flow.py:126`, `player/youtube/flow.py:182`, `player/youtube/search.py:22-35`.
- Reproduction or verification guidance: Manually set prefetch count to a large number and language/region to invalid or empty values, then run search and playlist prefetch.
- Recommended next action: Clamp prefetch getter/setter to 1-20 and validate language/region to safe defaults.
- Release-blocker status: No.

### YT-016: Controller shutdown does not clear YouTube sessions or prefetch executor

- Severity: Medium
- Category: risk
- Affected journey: cancellation and failure recovery, Windows integration
- Impact: Background YouTube prefetch/resolve work can outlive application shutdown unless it is cancelled through an explicit session cleanup path.
- Evidence: `specs/001-youtube-ultra-review/evidence/us1-playback-fallback.md`; current source `player/core/controller.py:432-453`, `player/youtube/flow.py:16-19`, `player/youtube/state.py:45-70`.
- Reproduction or verification guidance: Start prefetch/search/download work and close the app; inspect process lifetime and whether subprocesses/futures remain active.
- Recommended next action: Clear YouTube session on controller shutdown and add explicit module-level executor shutdown.
- Release-blocker status: No.

### YT-017: Current-source YouTube detection uses substring host matching

- Severity: Low
- Category: maintenance-note
- Affected journey: current video actions, downloads
- Impact: A non-YouTube host containing `youtube.com` or `youtu.be` could be treated as a YouTube current source.
- Evidence: `specs/001-youtube-ultra-review/evidence/us1-results-state.md`; current source `player/youtube/state.py:95-103`, stricter comparator `player/youtube/link_validator.py:45-52`.
- Reproduction or verification guidance: Set current source metadata to a host containing those substrings but not a valid YouTube host and inspect video option enablement.
- Recommended next action: Reuse strict host parsing from link validation for current-source checks.
- Release-blocker status: No.

### YT-018: Description lookup failures look like empty descriptions

- Severity: Low
- Category: risk
- Affected journey: current video actions, failure recovery
- Impact: Network or `yt-dlp` failure is indistinguishable from a valid video with no description.
- Evidence: `specs/001-youtube-ultra-review/evidence/us1-actions-entrypoints.md`; current source `player/youtube/video.py:24-36`, `player/youtube/video.py:76-90`, `player/youtube/video.py:105-111`.
- Reproduction or verification guidance: Trigger description lookup with network disabled and compare user feedback to a video that genuinely has no description.
- Recommended next action: Preserve a failure state and report Could not load description separately from No description.
- Release-blocker status: No.

### YT-019: Result list labels are title-only

- Severity: Low
- Category: missing-validation
- Affected journey: playlist browsing, accessibility feedback
- Impact: Duplicate or vague titles can be difficult to distinguish, especially for screen-reader users.
- Evidence: `specs/001-youtube-ultra-review/evidence/us2-accessibility-journey.md`; current source `player/youtube/results.py:116-119`, metadata source `player/youtube/resolver.py:12-18`, `player/youtube/search.py:98-110`.
- Reproduction or verification guidance: Search a query with duplicate titles and verify whether the list is distinguishable by keyboard and screen reader.
- Recommended next action: Include channel name and possibly item index/duration in result labels when available.
- Release-blocker status: No.

## Missing Validation

Manual checks not yet run:

- Fresh install startup prompt, skip checkbox, component install success/failure, and interrupted Deno extraction.
- YouTube search, direct link, playlist link, mixed link, invalid link, unavailable video, no-results, and rate-limit paths in a live Windows environment.
- Search result keyboard navigation, Enter behavior with button focus, copy/open browser/channel navigation, and return-to-results behavior with a screen reader.
- Natural EOF next-track behavior, explicit Next before/after prefetch, stale stream cache behavior, and local playback after YouTube failures.
- Download progress, cancellation, output folder behavior, and hung/blocked `yt-dlp` behavior.
- Windows SMTC/media-key behavior with MPV media controls and `WindowsMediaBridge` both active.
- App shutdown while search, resolve, prefetch, download, install, or update work is active.

Automated checks not yet available:

- Contract/report-shape validation for findings and evidence references.
- Link classification tests for invalid YouTube pages and mixed video/playlist URLs.
- Settings parsing/clamping tests for prefetch count, search language, and search region.
- Session state tests for Escape, targeted session cleanup, queued state, and next-track behavior.

Environment limitations:

- Review was based on source inspection and feature documents. Live YouTube network behavior, MPV playback, screen-reader announcements, helper binary install/update, and Windows media controls require manual validation on a configured Windows system.

## Remediation Sequence

### Release Blockers

1. REC-001: Fix session ownership and targeted cleanup for YouTube results dialogs.
2. REC-002: Synchronize YouTube session queued state with player source removal after Escape.
3. REC-003: Integrate YouTube next-track resolution with natural end-of-file handling.
4. REC-004: Make Deno install/extraction atomic and repair partial helper binaries.
5. REC-005: Decide whether MPV or `WindowsMediaBridge` owns Windows media controls.

### Important Hardening

1. REC-006: Reject unsupported YouTube URLs before stream resolution.
2. REC-007: Add user-facing feedback for background next, prefetch, and load-more failures.
3. REC-008: Add stream cache TTL or retry-on-open-failure re-resolution.
4. REC-009: Add subprocess timeout and terminate/wait/kill cleanup to resolver and downloads.
5. REC-010: Make missing-component search failure visible and actionable.
6. REC-011: Fix result dialog Enter handling to respect focused controls.
7. REC-012: Improve cancellation feedback and accessible progress reporting.
8. REC-013: Clarify or expand YouTube component update behavior.
9. REC-014: Clamp and validate settings-derived YouTube values.
10. REC-015: Clear YouTube sessions and stop background executors on shutdown.

### Future Improvements

1. REC-016: Reuse strict YouTube host validation for current-source checks.
2. REC-017: Distinguish description-load failure from no-description state.
3. REC-018: Add channel/index metadata to result labels for better accessibility.
4. REC-019: Consolidate duplicate task/busy dialog implementations.
