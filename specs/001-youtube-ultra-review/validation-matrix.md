# YouTube Ultra Review Validation Matrix

## Story 2 Validation Checklists

Journey coverage checklist:

- Search
- Direct link opening
- Playlist browsing
- Stream playback
- Next-track behavior
- Downloads
- Component setup/update
- Cancellation and failure recovery
- Accessibility feedback
- Local playback fallback

Journey row completeness checklist:

- Coverage status is one of `covered`, `partial`, `not-covered`, or `blocked`.
- Accessibility expectation is documented.
- Failure expectation is documented.
- Evidence reference is provided.
- Linked finding IDs are listed when applicable.

User-facing failure checklist:

- Expected spoken or visible feedback is documented.
- Recovery behavior is documented.
- Local playback fallback is documented where relevant.

## Matrix

| ID | Journey | Priority | Coverage Status | Accessibility Expectation | Failure Expectation | Evidence | Linked Findings |
|----|---------|----------|-----------------|---------------------------|---------------------|----------|-----------------|
| SCOPE-SEARCH | Search | P1 | partial | File > Search YouTube or Ctrl+Y opens a search prompt; progress and results should be keyboard-accessible and provide spoken/visible feedback. | Missing components, no results, network errors, and cancellation should explain recovery and leave local playback usable. | `evidence/us2-search-journey.md` | YT-007, YT-010, YT-012, YT-015 |
| SCOPE-DIRECT-LINK | Direct link opening | P1 | partial | File > Open YouTube Link or Ctrl+Shift+Y opens a link prompt and should reject unsupported input before long-running work. | Invalid, unsupported, removed, or unavailable links should produce visible/spoken feedback and preserve local playback. | `evidence/us2-direct-link-journey.md` | YT-006, YT-009 |
| SCOPE-PLAYLIST-LINK | Playlist and mixed links | P1 | partial | Mixed video-plus-playlist links should expose a keyboard-accessible chooser and clear feedback. | Invalid playlist entries and unavailable items should not leave stale session state. | `evidence/us2-playlist-link-journey.md` | YT-001, YT-007 |
| SCOPE-PLAYLIST-BROWSE | Playlist browsing and return to results | P1 | partial | Results dialog should support list navigation, Enter-to-play only from list focus, buttons, context menu, and screen-reader friendly labels. | Closing or returning from results should clean only the intended session and preserve active playback state. | `evidence/us2-playlist-browsing-journey.md` | YT-001, YT-011, YT-019 |
| SCOPE-STREAM-PLAYBACK | Stream playback | P1 | partial | Loading status should be visible/spoken; MPV should remain playback owner for stream loading. | Resolution failures, stale cached streams, and hung subprocesses should surface recovery guidance. | `evidence/us2-stream-playback-journey.md` | YT-008, YT-009 |
| SCOPE-NEXT-TRACK | Next-track behavior | P1 | partial | Next command should work from keyboard/menu and should provide progress/failure feedback. | Failed preload, unavailable next item, stale queued state, and natural EOF should be handled predictably. | `evidence/us2-next-track-preload-journey.md` | YT-002, YT-003, YT-007 |
| SCOPE-DOWNLOADS | Downloads | P2 | partial | Download action should be keyboard-accessible, expose destination selection, and report progress/cancel outcomes. | Download failure, cancel, or hung `yt-dlp` should not block the UI or leave ambiguous output state. | `evidence/us2-download-journey.md` | YT-009, YT-012, YT-013 |
| SCOPE-COMPONENTS | Component setup/update | P2 | partial | Startup/install/update prompts should be keyboard-accessible and provide spoken/visible status. | Missing, outdated, blocked, partial, or failed helpers should offer repair/retry and keep local playback usable. | `evidence/us2-helper-component-journey.md` | YT-004, YT-010, YT-014 |
| SCOPE-CANCELLATION | Cancellation and failure recovery | P1 | partial | Cancel should be available through keyboard and should announce or visibly confirm the result. | Canceled or failed search/load/download/update/preload should clear pending state and stop or safely wind down background work. | `evidence/us2-cancellation-recovery-journey.md` | YT-007, YT-009, YT-012, YT-016 |
| SCOPE-A11Y | Accessibility feedback | P1 | partial | Keyboard paths, menus, dialog controls, and spoken/visible feedback should remain consistent. | Silent failures, duplicate feedback, and focus-stealing shortcuts should be avoided. | `evidence/us2-accessibility-journey.md` | YT-010, YT-011, YT-013, YT-019 |
| SCOPE-LOCAL-FALLBACK | Local playback fallback | P1 | partial | Local file playback should remain usable after YouTube failures and Windows media integration should degrade safely. | YouTube helper/network/platform failures should not block local playback or leave stale YouTube state. | `evidence/us2-local-playback-fallback.md` | YT-005, YT-016 |

## Quickstart Flow Coverage

- Search for YouTube content: SCOPE-SEARCH.
- Open a direct video link: SCOPE-DIRECT-LINK.
- Open a playlist link: SCOPE-PLAYLIST-LINK.
- Handle mixed video-plus-playlist links: SCOPE-PLAYLIST-LINK.
- Browse results and return to results from playback: SCOPE-PLAYLIST-BROWSE.
- Play current item and move to the next item: SCOPE-STREAM-PLAYBACK, SCOPE-NEXT-TRACK.
- Download the current YouTube item: SCOPE-DOWNLOADS.
- Install or update helper components: SCOPE-COMPONENTS.
- Cancel active search, load, download, update, or preload work: SCOPE-CANCELLATION.
- Recover from invalid links, no results, unavailable videos, and rate limits: SCOPE-DIRECT-LINK, SCOPE-SEARCH, SCOPE-CANCELLATION.
