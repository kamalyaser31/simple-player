# Helper Component and Settings Surface

- Evidence ID: EVID-FOUNDATION-012
- Type: source-inspection
- Result: risk

## Current Surface

- `player/youtube/components.py:13-16` defines app-local `yt-dlp.exe`, `deno.exe`, and `deno.zip` paths.
- `player/youtube/components.py:56-65` treats helper availability as file existence.
- `player/youtube/components.py:142-162` installs missing helpers.
- `player/youtube/components.py:165-178` updates only existing yt-dlp.
- `player/youtube/startup.py:17-37` prompts on startup if helpers are missing and the prompt is not skipped.
- `player/config/settings_manager.py:110-120` sets YouTube defaults.
- `player/config/settings_manager.py:365-400` parses prefetch count and search locale without range/format validation beyond integer conversion and stripping.
- `player/ui/prefs/youtube.py:46-48` constrains prefetch to 1-20 in the UI only.

## Risks

- Partial helper binaries can pass availability checks.
- Update action does not update or repair all YouTube components.
- Manual config edits can bypass UI constraints.
