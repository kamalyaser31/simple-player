# Feature Specification: Fix YouTube Release Blockers

**Feature Branch**: `main`

**Created**: 2026-07-06

**Status**: Draft

**Input**: User description: "fix all critical"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preserve YouTube Playback Session Continuity (Priority: P1)

As a keyboard-first listener, I want YouTube search and playlist playback to keep the correct session state when I browse results, return from playback, and move to the next item so that YouTube playback does not lose context or stop unexpectedly.

**Why this priority**: Three release blockers affect the core daily playback journey: closing a results dialog can clear the wrong session, returning to results can leave stale queued state, and natural end-of-file playback can fail to continue through unresolved next items.

**Independent Test**: A tester can start playback from a YouTube search or playlist with at least three playable items, open and close another results view, return to the original results, use explicit Next, and let playback naturally advance without losing the active session or stopping prematurely.

**Acceptance Scenarios**:

1. **Given** a YouTube item is playing from a results session, **When** the user opens and closes another YouTube results view without playing from it, **Then** the original playback session remains available for return-to-results and next-track behavior.
2. **Given** a user returns from YouTube playback to the results list, **When** the user requests the next item, **Then** the next item is prepared from the current session rather than relying on stale queue state.
3. **Given** a YouTube search or playlist has additional playable items, **When** the current item reaches the end naturally, **Then** playback advances to the next item or provides clear feedback if the next item cannot be played.

---

### User Story 2 - Prevent Broken Helper Components From Appearing Ready (Priority: P1)

As a user who installs YouTube helper components, I want interrupted or failed component setup to leave the application in a clearly recoverable state so that broken helper files are not treated as usable.

**Why this priority**: A partial helper executable can make YouTube features appear available while still failing later, which blocks reliable recovery from install or update problems.

**Independent Test**: A tester can interrupt helper component setup during extraction or replacement, restart the application, and verify that YouTube features detect the component as missing or broken and offer a safe recovery path while local playback remains usable.

**Acceptance Scenarios**:

1. **Given** helper component setup is interrupted, **When** the application checks component readiness, **Then** any partial or unusable helper is not reported as ready.
2. **Given** helper component setup fails, **When** the user starts a YouTube action, **Then** the user receives clear visible or spoken recovery guidance.
3. **Given** helper component setup fails, **When** the user plays local media, **Then** local playback remains usable.

---

### User Story 3 - Ensure One Windows Media Control Owner (Priority: P2)

As a Windows user with media keys or system media controls, I want media commands to be handled once and reflected consistently so that playback controls do not duplicate, conflict, or report stale media state.

**Why this priority**: Conflicting media-control ownership can affect both YouTube and local playback, but it is platform-specific and can be validated independently after core playback continuity is fixed.

**Independent Test**: A tester can play local and YouTube media on Windows, use hardware media keys and system media controls, and verify that each command produces exactly one playback action and one coherent media status.

**Acceptance Scenarios**:

1. **Given** media is playing on Windows, **When** the user presses Play/Pause, Next, or Previous through system media controls, **Then** each command changes playback once and only once.
2. **Given** local playback and YouTube playback are both tested, **When** media status is displayed by Windows, **Then** the displayed title, playback status, and available commands remain consistent with the current item.
3. **Given** Windows media integration is unavailable or fails, **When** the user uses the application normally, **Then** local playback and keyboard controls continue to work.

---

### Edge Cases

- What happens when a second YouTube results view is opened while another YouTube item is already playing?
- What happens when the user closes a results view that has background work in progress?
- What happens when the user returns to results after removing session-owned playback items?
- What happens when the next YouTube item is unavailable, removed, or cannot be prepared before the current item ends?
- What happens when helper component setup is cancelled during download, extraction, or replacement?
- What happens when a helper component file exists but cannot run successfully?
- What happens when Windows media controls are unavailable, disabled, or fail during playback?

### Accessibility and Platform Expectations *(mandatory for UI/playback changes)*

- **Keyboard path**: YouTube search, opening links, browsing results, returning to results, explicit Next, and local playback controls must remain usable from keyboard and menu paths.
- **Feedback**: Playback continuation, failed next-item recovery, helper setup failure, helper repair prompts, and Windows integration fallback must provide clear spoken or visible feedback without duplicate announcements.
- **Windows integration**: Media keys and system media status must have one effective control owner, degrade safely when unavailable, and never make local playback unusable.
- **Failure behavior**: YouTube session, helper component, or Windows integration failures must not corrupt local playback state, block local files from playing, or leave stale YouTube session state visible to the user.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST fix all release blockers identified by the YouTube Ultra Review as YT-001 through YT-005.
- **FR-002**: The system MUST preserve the active YouTube playback session when a user opens and closes a separate results view without switching playback to that view.
- **FR-003**: The system MUST ensure returning from YouTube playback to results does not leave stale next-item or queued-item state.
- **FR-004**: The system MUST continue YouTube search or playlist playback to the next playable item when the current item ends naturally.
- **FR-005**: The system MUST provide clear user feedback when the next YouTube item cannot be played.
- **FR-006**: The system MUST ensure interrupted helper component setup cannot leave a partial or unusable helper component reported as ready.
- **FR-007**: The system MUST provide a safe recovery path when helper component setup, repair, or readiness checking fails.
- **FR-008**: The system MUST keep local playback usable when YouTube helper components are missing, broken, interrupted, or being repaired.
- **FR-009**: The system MUST ensure Windows media controls have one effective owner for playback commands and media status.
- **FR-010**: The system MUST ensure each Windows media command triggers no more than one playback action.
- **FR-011**: The system MUST preserve keyboard-first operation and accessible feedback for every changed UI or playback action.
- **FR-012**: The system MUST document validation evidence for each fixed release blocker before the feature is considered complete.

### Key Entities *(include if feature involves data)*

- **YouTube Playback Session**: The active user context for YouTube results, playback, return-to-results behavior, queued items, pending next item, and background work.
- **Queued YouTube Item**: A YouTube item that the session expects to be available for current or future playback.
- **Helper Component**: A required local component used for YouTube functionality, with states such as missing, installing, ready, broken, or repair required.
- **Windows Media Control State**: The user-visible media status and accepted media commands exposed through Windows controls.
- **Release Blocker Validation Record**: Evidence that a specific release blocker has been fixed and independently verified.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of YouTube Ultra Review release blockers YT-001 through YT-005 are validated as fixed with recorded evidence.
- **SC-002**: In 3 consecutive validation runs, a YouTube search or playlist with at least 3 playable items can continue through explicit Next and natural end-of-item advancement without losing the active session.
- **SC-003**: In 3 interruption scenarios during helper component setup, the application never reports a partial or unusable helper component as ready.
- **SC-004**: In 5 consecutive Windows media-control checks, each Play/Pause, Next, or Previous command produces exactly one playback action.
- **SC-005**: 100% of affected keyboard and menu paths remain usable without a mouse during validation.
- **SC-006**: 100% of validated failure paths provide clear spoken or visible feedback and leave local playback usable.

## Assumptions

- "Critical" refers to the five release blockers listed in `specs/001-youtube-ultra-review/youtube-ultra-review.md`: YT-001 through YT-005.
- Medium and low findings from the review are out of scope unless needed to safely fix a release blocker.
- Existing YouTube user journeys, shortcuts, and menu paths should remain recognizable to users.
- Manual validation is acceptable for live YouTube playback, helper component setup, screen-reader behavior, and Windows media-control behavior.
- The feature should avoid unrelated refactors and should preserve local playback behavior while YouTube issues are being fixed.
