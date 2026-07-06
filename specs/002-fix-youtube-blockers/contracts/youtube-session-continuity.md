# Contract: YouTube Session Continuity

## Scope

This contract covers release blockers YT-001, YT-002, and YT-003 for YouTube search and
playlist sessions.

## Required Behaviors

1. Opening a second YouTube results view while another YouTube item is playing must not
   clear or overwrite the active playback session unless the user starts playback from
   the second view.
2. Closing a results view must only cancel background work owned by that view's session.
3. Returning from playback to results must leave the session in a state where explicit
   Next can prepare or play the correct next item.
4. Removing session-owned player sources must clear or invalidate matching queued state.
5. Natural end-of-item playback for a YouTube session must attempt to advance to the next
   playable item.
6. If the next item cannot be prepared or played, the user must receive clear spoken or
   visible feedback and local playback must remain usable.

## Acceptance Checks

- Start YouTube playback from a results session, open and close another results view, and
  verify the original session still supports return-to-results and Next.
- Play a YouTube item, return to results, press Next, and verify the next item is prepared
  from current session state rather than stale queued state.
- Play a YouTube search or playlist with at least three playable items and verify natural
  end-of-item advancement across the sequence.
- Force or simulate an unavailable next item and verify user feedback plus local playback
  fallback.

## Evidence Required

- Validation record for YT-001 session ownership.
- Validation record for YT-002 queued-state synchronization.
- Validation record for YT-003 natural EOF advancement.
