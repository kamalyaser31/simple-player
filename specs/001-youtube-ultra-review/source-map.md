# YouTube Ultra Review Source Map

## Review Authority

Current behavior is the only review authority. Current source, current project documentation, and observed behavior can be used as evidence. Stale historical plans are excluded as standalone evidence because they can misrepresent current risks and priorities.

## Core YouTube Modules

| File | Review Role | Notes |
|------|-------------|-------|
| `player/youtube/actions.py` | Public action export facade | Re-exports flow/video actions; no behavior beyond API surface. |
| `player/youtube/flow.py` | Primary YouTube orchestration | Link open, search, session display, playback prep, prefetch, next handling, cache, Escape. |
| `player/youtube/search.py` | Search adapter | Wraps `py_yt.VideosSearch`, item conversion, load-more. |
| `player/youtube/link_validator.py` | URL classification | Parses YouTube hosts, video IDs, playlist IDs, invalid/mixed/channel states. |
| `player/youtube/resolver.py` | yt-dlp stream resolution | Runs helper subprocesses, handles format selection, 429 diagnostics, metadata. |
| `player/youtube/results.py` | Results dialog controller | Dialog actions, load-more, prefetch start, cleanup on close. |
| `player/youtube/state.py` | Session and current-source state | Session creation/cleanup, source detection, cancellation. |
| `player/youtube/download.py` | Audio download worker | Runs yt-dlp extraction, parses progress, cancellation callback. |
| `player/youtube/components.py` | Helper install/update | Installs yt-dlp and Deno, updates yt-dlp, availability checks. |
| `player/youtube/startup.py` | Startup missing-component prompt | PATH setup, prompt, manual install. |
| `player/youtube/task_ui.py` | YouTube task wrapper | Modal task dialog, worker thread, cancel flag. |
| `player/youtube/ui_utils.py` | YouTube UI helpers | Input prompts, mixed-link chooser, error dialogs, progress text. |
| `player/youtube/video.py` | Current video actions | Description, download current, copy link. |

## Cross-Cutting Surfaces

| Area | Files | Review Role |
|------|-------|-------------|
| UI/accessibility | `player/ui/yt_dialogs.py`, `player/ui/task_dialogs.py`, `player/ui/main_frame.py`, `player/speech.py` | Dialog controls, accelerators, spoken feedback, accessible progress. |
| Action/menu routing | `player/actions.py`, `player/ui/mainwin/menu.py`, `player/core/controller.py` | Menu paths, shortcuts, controller dispatch. |
| Playback/control | `player/core/controller.py`, `player/core/action_context.py`, `player/core/player/`, `player/core/mpv_engine.py` | MPV ownership, local playback, EOF behavior, action context. |
| Windows media | `player/core/windows_media.py` | SMTC/media-key bridge, safe degradation. |
| Settings | `player/config/settings_manager.py`, `player/config/constants.py`, `player/ui/prefs/youtube.py` | YouTube defaults, validation, preferences UI. |
| Updates | `player/update/actions.py` | yt-dlp version check/update, user feedback. |

## Evidence Rules

- File and line references point to current source inspected during this review.
- `not-run` evidence is acceptable for manual GUI/playback/Windows checks but cannot be sole support for confirmed defects.
- Each finding maps to at least one current-source evidence file under `specs/001-youtube-ultra-review/evidence/`.
