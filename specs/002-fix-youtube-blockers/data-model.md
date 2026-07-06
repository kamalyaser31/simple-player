# Data Model: Fix YouTube Release Blockers

## YouTube Playback Session

Represents the active or displayed YouTube search/playlist context used for playback,
return-to-results behavior, prefetch, explicit Next, and natural end-of-item advancement.

**Fields**:

- `session_id`: Stable identity for the session during its lifetime.
- `items`: Ordered playable/search result items associated with the session.
- `active_index`: Current item index or no current item.
- `display_owner`: Whether a results view owns cleanup for this session.
- `playback_owner`: Whether this session is the active playback session.
- `queued_items`: Items actually available or expected to be available for playback.
- `pending_next`: Next item currently being prepared, if any.
- `background_jobs`: Prefetch or resolve work associated with this session.
- `cancel_state`: Active, cancel requested, canceled, or completed.

**Validation rules**:

- Closing a non-playback results view must not clear another active playback session.
- Cleanup must cancel only jobs associated with the session being cleaned up.
- `queued_items` must not claim availability for sources removed from the player.
- Natural end-of-item advancement must use the current active playback session.

## Queued YouTube Item

Represents a YouTube item that can be used for explicit Next or natural playback advance.

**Fields**:

- `source_url`: Original YouTube URL.
- `title`: User-visible title.
- `stream_state`: unresolved, resolving, ready, failed, or removed.
- `player_source_state`: queued, playing, removed, or absent.
- `failure_feedback`: Spoken or visible message when the item cannot be prepared.

**Validation rules**:

- Ready queued items must correspond to a playable source or a resolvable pending item.
- Removed player sources must clear or invalidate queued item state.
- Failed next items must provide user-facing feedback and not block local playback.

## Helper Component

Represents a local YouTube helper binary required for YouTube workflows.

**Fields**:

- `name`: Helper name, such as yt-dlp or Deno.
- `expected_path`: Expected local path.
- `state`: missing, installing, ready, broken, repair-required, or update-available.
- `last_operation`: install, update, repair, cancel, or validation.
- `operation_result`: success, failure, canceled, or not-run.
- `recovery_message`: User-facing recovery guidance when not ready.

**Validation rules**:

- Partial files must not be reported as ready.
- Replacement must leave either the previous valid helper or a clean non-ready state.
- Broken or missing helpers must not block local playback.
- Recovery guidance must be visible or spoken for YouTube actions that require helpers.

## Windows Media Control State

Represents media-key and system media status ownership on Windows.

**Fields**:

- `owner`: Selected effective owner for Windows media commands and status.
- `status`: playing, paused, stopped, unavailable, or disabled.
- `current_title`: Title shown to Windows controls.
- `available_commands`: Commands exposed through Windows controls.
- `fallback_state`: disabled, unavailable, failed-safe, or active.

**Validation rules**:

- Exactly one effective owner handles Play/Pause, Next, and Previous commands.
- Each media command triggers no more than one playback action.
- Integration failure must leave keyboard controls and local playback usable.

## Release Blocker Validation Record

Represents evidence that one release blocker is fixed.

**Fields**:

- `blocker_id`: YT-001 through YT-005.
- `scenario`: User story or edge case validated.
- `method`: automated-check or manual-check.
- `result`: pass, fail, blocked, or not-run.
- `evidence`: Concise observation and relevant artifact reference.
- `limitations`: Environment or manual validation limitations.

**Validation rules**:

- Every blocker must have at least one passing validation record.
- Playback continuity blockers require explicit Next and natural EOF validation.
- Helper integrity requires interrupted setup validation.
- Windows media ownership requires Windows manual validation.

## Relationships

- One YouTube Playback Session has many Queued YouTube Items.
- One YouTube Playback Session can have many Release Blocker Validation Records.
- One Helper Component can have many validation records across install, update, repair,
  and readiness checks.
- One Windows Media Control State has validation records for local playback, YouTube
  playback, media keys, and fallback.

## State Transitions

YouTube Playback Session:

```text
displayed -> playback-active -> returning-to-results -> playback-active
displayed -> closed -> cleaned-up
playback-active -> cancel-requested -> cleaned-up
```

Queued YouTube Item:

```text
unresolved -> resolving -> ready -> playing
unresolved -> resolving -> failed
ready -> removed
```

Helper Component:

```text
missing -> installing -> ready
missing -> installing -> repair-required
ready -> update-available -> installing -> ready
ready -> installing -> broken -> repair-required
```

Windows Media Control State:

```text
unavailable -> disabled
unavailable -> active
active -> failed-safe
active -> disabled
```
