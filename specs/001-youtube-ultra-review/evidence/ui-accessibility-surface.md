# UI and Accessibility Surface

- Evidence ID: EVID-FOUNDATION-010
- Type: source-inspection
- Result: risk

## Current Surface

- `player/actions.py:166-175` defines Open YouTube Link and Search YouTube actions with default shortcuts.
- `player/ui/mainwin/menu.py:132-139` and `player/ui/mainwin/menu.py:181-182` expose the File menu paths and bindings.
- `player/core/controller.py:267-272` dispatches YouTube actions to the YouTube flow/video modules.
- `player/youtube/ui_utils.py:26-51` provides text prompts for open-link and search.
- `player/ui/yt_dialogs.py:152-185` builds the results dialog controls and context menu.
- `player/ui/yt_dialogs.py:238-268` installs dialog accelerators and an Enter handler.
- `player/youtube/results.py:54-79`, `player/youtube/results.py:139-141`, and `player/youtube/video.py:16-73` provide spoken feedback for selected operations.
- `player/ui/task_dialogs.py:12-18` and `player/ui/task_dialogs.py:76-78` define shared task dialog controls used by YouTube task UI.

## Risks

- Results dialog Enter handling can override focused buttons.
- Missing-components behavior differs between search and open-link.
- Task dialogs update visual controls but do not provide accessible progress announcements.
