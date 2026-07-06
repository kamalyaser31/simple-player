# Contract: Windows Media Control Ownership

## Scope

This contract covers release blocker YT-005 for Windows system media controls, hardware
media keys, and playback status.

## Required Behaviors

1. There must be one effective owner for Windows media commands and media status.
2. Play/Pause, Next, and Previous commands from Windows controls must trigger exactly one
   playback action per command.
3. Windows media status must reflect the current local or YouTube item without duplicate
   sessions or stale status.
4. If Windows media integration is unavailable or fails, the application must keep local
   playback and keyboard controls usable.
5. The chosen ownership model must preserve MPV playback ownership while keeping wxPython
   and controller action flow responsible for user commands.

## Acceptance Checks

- Play local media and verify Play/Pause, Next, and Previous through Windows controls.
- Play YouTube media and verify the same commands.
- Inspect Windows media display for duplicate sessions or stale titles/status.
- Disable or simulate unavailable Windows media integration and verify local playback and
  keyboard controls still work.

## Evidence Required

- Validation record showing one action per Windows media command.
- Validation record showing local and YouTube media status consistency.
- Validation record showing safe fallback when Windows media integration is unavailable.
