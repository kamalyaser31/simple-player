# Research: Fix YouTube Release Blockers

## Decision: Treat the Five Release Blockers as the Complete Critical Scope

**Rationale**: The user asked to fix all critical items after the YouTube Ultra Review.
The review labels five high-severity release blockers: YT-001 through YT-005. Limiting
scope prevents medium and low hardening items from expanding the release-blocker fix into
a broad refactor.

**Alternatives considered**: Include every high, medium, and low review finding. Rejected
because the request was critical/release-blocker focused and broader work would reduce
independent validation clarity.

## Decision: Make Results Dialog Session Ownership Explicit

**Rationale**: YT-001 exists because a displayed results session can start prefetch work
and later close by clearing whichever session is currently stored on the context. The
safe behavior is for each results view to know whether it owns the active playback
session and to clean up only the session it is responsible for.

**Alternatives considered**: Always clear the current context session on any results
dialog close. Rejected because it can destroy an unrelated active playback session.

## Decision: Synchronize Queued State Whenever Session-Owned Sources Are Removed

**Rationale**: YT-002 exists because Escape can remove session-owned player sources while
the session still marks items as queued. Queue state should represent what can actually
play next, not stale intent.

**Alternatives considered**: Leave queued state untouched and rely on future playback
errors. Rejected because it makes explicit Next unreliable and hard to diagnose.

## Decision: Integrate YouTube Next Behavior With Natural End-of-Item Playback

**Rationale**: YT-003 exists because generic end-of-item behavior only advances through
already queued player state, while YouTube next items may need resolution. Natural EOF
should either prepare the next YouTube item or provide clear failure feedback.

**Alternatives considered**: Require users to press Next manually for YouTube playlists.
Rejected because the success criteria require natural advancement and the feature is a
daily playback workflow.

## Decision: Use Atomic Helper Replacement for Deno Integrity

**Rationale**: YT-004 exists because Deno extraction can write directly to the final
executable path. Helper readiness should not be based on a partial file. Atomic temporary
replacement keeps the previous ready helper or a clean missing/broken state.

**Alternatives considered**: Keep file-existence readiness checks only. Rejected because
partial binaries can pass readiness while failing at use time.

## Decision: Make Custom WindowsMediaBridge the Single Windows Media Owner Unless Rejected by Implementation Evidence

**Rationale**: The project already owns a guarded custom Windows media bridge with safe
fallback behavior and controller-level action routing. MPV should remain playback owner,
but Windows media controls should have one command/status owner to avoid duplicate media
sessions and duplicate key handling.

**Alternatives considered**: Use both MPV media controls and custom SMTC. Rejected because
the release blocker is about duplicate/conflicting ownership. Use MPV only was considered
but would bypass project-specific controller feedback and bridge fallback behavior.

## Decision: Prefer Focused Automated State Checks Plus Manual Integration Validation

**Rationale**: Session cleanup, queue synchronization, helper readiness classification,
and media-control ownership can be validated partly through deterministic checks, while
wxPython UI, MPV playback, helper interruption, screen-reader feedback, and Windows media
keys require manual validation on Windows.

**Alternatives considered**: Manual-only validation. Rejected because pure state behavior
can regress and should be verified repeatably. Full automation of playback/SMTC was
rejected as impractical for this planning phase.
