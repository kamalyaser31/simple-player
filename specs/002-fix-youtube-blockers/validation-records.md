# Validation Records: Fix YouTube Release Blockers

## Record Format

- `blocker_id`: YT-001 through YT-005
- `scenario`: User story or edge case validated
- `method`: automated-check or manual-check
- `result`: pass, fail, blocked, or not-run
- `evidence`: Concise observation and relevant artifact reference
- `limitations`: Environment or manual validation limitations

## YT-001: Secondary Results Close Preserves Active Session

- `method`: automated-check
- `result`: pass
- `evidence`: `python -m pytest tests` passed. `tests/test_youtube_session_continuity.py` verifies secondary session cleanup leaves the active playback session intact and cancels only supplied-session jobs.
- `limitations`: Pure state/fake player validation only.
- `method`: manual-check
- `result`: not-run
- `evidence`: Open a secondary YouTube results view while original playback is active, close it, then return to original results and use Next.
- `limitations`: Requires wxPython, network YouTube playback, and MPV runtime.

## YT-002: Return-To-Results Queue State Synchronization

- `method`: automated-check
- `result`: pass
- `evidence`: `python -m pytest tests` passed. `tests/test_youtube_session_continuity.py` verifies removed session-owned sources clear matching queued and pending-next state, and stale queued state is revalidated before explicit Next.
- `limitations`: Pure state/fake player validation only.
- `method`: manual-check
- `result`: not-run
- `evidence`: During YouTube playback, press Escape to return to results, then use explicit Next.
- `limitations`: Requires wxPython, network YouTube playback, and MPV runtime.

## YT-003: Natural End-Of-Item YouTube Advancement

- `method`: automated-check
- `result`: pass
- `evidence`: `python -m pytest tests` passed. `tests/test_youtube_session_continuity.py` verifies natural EOF calls the active YouTube next handler and preserves playback state when next preparation is pending/unavailable.
- `limitations`: Pure state/fake player validation only; live natural EOF playback still needs manual MPV validation.
- `method`: manual-check
- `result`: not-run
- `evidence`: Let a YouTube search or playlist advance naturally through at least three playable items; verify unavailable next item feedback.
- `limitations`: Requires live playback and suitable YouTube items.

## YT-004: Helper Component Integrity

- `method`: automated-check
- `result`: pass
- `evidence`: `python -m pytest tests` passed. `tests/test_youtube_component_integrity.py` verifies partial Deno is not ready, failed extraction preserves prior Deno, cancellation cleans temp files, and recovery guidance is present.
- `limitations`: Filesystem/zip validation only; live interrupted installer validation still needs manual run.
- `method`: manual-check
- `result`: not-run
- `evidence`: Interrupt Deno extraction or helper setup, restart, verify non-ready state and recovery guidance, then play a local file.
- `limitations`: Requires controlled helper setup interruption.

## YT-005: One Windows Media Control Owner

- `method`: automated-check
- `result`: pass
- `evidence`: `python -m pytest tests` passed. `tests/test_windows_media_ownership.py` verifies MPV media controls/media keys are disabled for custom bridge ownership, unavailable winsdk fallback is safe, and one simulated bridge callback emits one action.
- `limitations`: Simulated bridge validation only; real Windows media controls/SMTC still need manual desktop validation.
- `method`: manual-check
- `result`: not-run
- `evidence`: Use Play/Pause, Next, and Previous via Windows media controls for local and YouTube playback; verify one coherent status session and fallback when unavailable.
- `limitations`: Requires Windows SMTC/media key validation.

## Scope Verification

- Medium and low YouTube Ultra Review findings are intentionally out of scope unless required for YT-001 through YT-005.

## Lifecycle Entry Points

- `player/youtube/flow.py`: Creates search/playlist sessions, promotes playback ownership through `_play_item`, handles Escape return-to-results, explicit Next, prefetch, and natural EOF via `on_playback_finished`.
- `player/youtube/results.py`: Owns displayed results dialog cleanup and now targets only the displayed session.
- `player/youtube/state.py`: Owns current session storage, targeted cleanup, cancellation, and removed-source queue synchronization.

## Windows Media Ownership Decision

- Selected owner: `player/core/windows_media.py` custom `WindowsMediaBridge`.
- MPV remains playback owner, but `player/core/mpv_engine.py` disables MPV-owned Windows media controls and input media keys to prevent duplicate command/status ownership.

## Automated Test Suite

- `method`: automated-check
- `result`: pass
- `evidence`: `python -m pytest tests` -> 14 passed.
- `limitations`: Covers release-blocker pure state/helper/media-ownership checks only.

## Quickstart Artifact Validation

- `method`: automated-check
- `result`: pass
- `evidence`: Required quickstart planning artifacts exist: spec, plan, research, data model, contracts directory, tasks, and validation records.
- `limitations`: Artifact existence/scope validation only.

## Keyboard, Feedback, And Local Playback Regression Notes

- Keyboard/menu paths remain routed through existing action handlers for YouTube search, open link, result browsing, Escape return-to-results, and explicit Next.
- Failed next-item preparation now speaks visible/screen-reader feedback through `ctx.speak` without clearing local playback state.
- Broken helper checks return recovery guidance before YouTube actions mutate playback state.
- Local playback EOF handling keeps the existing non-YouTube path when no active YouTube session handles the finished file.

## Local Playback Regression

- `method`: automated-check
- `result`: pass
- `evidence`: `tests/test_youtube_session_continuity.py::test_non_youtube_eof_keeps_existing_local_advance_behavior` verifies non-YouTube EOF still advances through the existing local playback path when the YouTube hook does not handle the event.
- `limitations`: Fake lifecycle state only; real MPV local playback remains a manual validation item.

## Constitution Compliance Check

- Accessibility and keyboard control: pass for code-level checks; manual screen-reader validation remains not-run.
- MVC/action boundaries: pass; changes stay within `youtube/`, `core/player/`, `core/`, playlist state metadata, and existing action routing.
- Windows fallback: pass for guarded unavailable-bridge automated test; real SMTC validation remains not-run.
- Local data integrity: pass; Deno replacement is temporary-file plus atomic replace and does not overwrite the prior valid helper on extraction failure.
- Responsiveness/verifiability: pass for preserving existing background jobs and adding targeted automated tests; live wxPython/MPV validation remains not-run.
