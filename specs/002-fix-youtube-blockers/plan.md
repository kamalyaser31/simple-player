# Implementation Plan: Fix YouTube Release Blockers

**Branch**: `main` | **Date**: 2026-07-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-fix-youtube-blockers/spec.md`

## Summary

Fix the five YouTube Ultra Review release blockers by tightening session ownership,
queue-state synchronization, natural next-track playback, helper-component integrity,
and Windows media-control ownership. The implementation will stay within existing
YouTube flow/component modules and core playback/media-control boundaries, with manual
validation for wxPython, MPV, helper binaries, screen-reader behavior, and Windows SMTC.

## Technical Context

**Language/Version**: Python 3.11 or newer recommended by project documentation

**Primary Dependencies**: wxPython desktop UI, libmpv through the Python MPV binding,
yt-dlp and Deno helper components for YouTube workflows, Windows media APIs through
optional `winsdk`

**Storage**: App-local helper binaries under `player/`; transient YouTube playback
session state in memory; no user data migration planned

**Testing**: Targeted automated checks for pure session/helper state where practical;
manual validation for wxPython UI, MPV playback, helper install interruption,
screen-reader feedback, and Windows media controls

**Target Platform**: Windows desktop application

**Project Type**: Desktop media player

**Performance Goals**: YouTube playlist/search playback advances through at least three
items without losing session state; helper readiness checks complete quickly enough that
YouTube actions give feedback without blocking the UI; Windows media commands trigger
exactly one playback action per command

**Constraints**: Preserve keyboard-first access and accessible feedback; preserve MPV
ownership of playback state; keep local playback usable when YouTube helpers or Windows
integration fail; avoid broad refactors outside the release-blocker scope

**Scale/Scope**: Five release blockers from `specs/001-youtube-ultra-review/` covering
YouTube session cleanup, queued state, natural next playback, Deno helper integrity, and
single Windows media-control ownership

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Accessibility and keyboard control**: PASS. The spec defines keyboard/menu paths for
   YouTube search, link opening, result browsing, return-to-results, explicit Next, and
   local playback controls. The plan requires spoken or visible feedback for failed
   next-item recovery, helper setup failure, and Windows fallback.
2. **Architecture boundaries**: PASS. Planned changes remain in `player/youtube/` for
   YouTube session/helper behavior, `player/core/player/` for natural playback/EOF
   behavior, and `player/core/` for media-control ownership. UI changes are limited to
   existing feedback paths if needed.
3. **Windows integration safety**: PASS. The Windows media-control release blocker is
   explicitly scoped to one effective owner, safe fallback, and local playback continuity.
4. **Local data integrity**: PASS. No settings/bookmark/favorites/positions migration is
   planned. Helper binary replacement must be atomic and must not leave partial files
   reported as ready.
5. **Responsiveness and verification**: PASS. The plan requires existing worker/cancel
   patterns for helper work and validation for playback, accessibility feedback,
   helper interruption, and Windows media boundaries.

## Project Structure

### Documentation (this feature)

```text
specs/002-fix-youtube-blockers/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── youtube-session-continuity.md
│   ├── helper-component-integrity.md
│   └── windows-media-control.md
└── tasks.md
```

### Source Code (repository root)

```text
player/
├── youtube/
│   ├── flow.py              # Session ownership, Escape, prefetch, next-track handoff
│   ├── results.py           # Results dialog close behavior and prefetch lifecycle
│   ├── state.py             # Session cleanup/cancellation and current session state
│   ├── components.py        # Helper availability, install, atomic Deno replacement
│   ├── startup.py           # Missing/broken helper recovery prompts if needed
│   └── task_ui.py           # Existing task/cancellation pattern for helper work
├── core/
│   ├── controller.py        # Shutdown, action routing, Windows media bridge ownership
│   ├── mpv_engine.py        # MPV media-control option ownership decision
│   ├── windows_media.py     # Custom SMTC bridge fallback behavior
│   └── player/
│       ├── lifecycle.py     # Natural end-of-item behavior
│       └── load.py          # Stream metadata/source tracking
├── app_actions/
│   └── file_actions.py      # Explicit Next path interaction with YouTube next behavior
└── ui/
    └── mainwin/menu.py      # Existing keyboard/menu paths; no broad UI redesign planned
```

**Structure Decision**: YouTube-specific state and helper integrity stay under
`player/youtube/`; natural EOF integration stays in the core player lifecycle because it
is triggered by playback completion; Windows media ownership stays in `player/core/`
because both MPV and the custom bridge are initialized there. This preserves existing MVC
and action-dispatch boundaries while limiting the change to release blockers.

## Phase 0: Research

Research output is captured in [research.md](./research.md). Decisions resolve session
ownership, queued-state synchronization, next-track EOF behavior, helper binary integrity,
Windows media-control ownership, and validation strategy.

## Phase 1: Design & Contracts

Design artifacts:

- [data-model.md](./data-model.md): YouTube playback session, queued item, helper
  component, Windows media control state, and validation record entities.
- [contracts/youtube-session-continuity.md](./contracts/youtube-session-continuity.md):
  Behavioral contract for result dialog ownership, Escape, explicit Next, and natural EOF.
- [contracts/helper-component-integrity.md](./contracts/helper-component-integrity.md):
  Behavioral contract for helper readiness, interrupted setup, and recovery.
- [contracts/windows-media-control.md](./contracts/windows-media-control.md): Behavioral
  contract for single media-control ownership and safe fallback.
- [quickstart.md](./quickstart.md): End-to-end validation guide for the release blockers.

Agent context update: skipped because this Spec Kit installation does not include an
agent-context update script under `.specify/scripts/`.

## Post-Design Constitution Check

1. **Accessibility and keyboard control**: PASS. Contracts and quickstart include keyboard
   and spoken/visible feedback validation for affected YouTube and media-control paths.
2. **Architecture boundaries**: PASS. Design artifacts map each behavior to existing
   `youtube/`, `core/player/`, and `core/` ownership boundaries without introducing a new
   cross-cutting abstraction.
3. **Windows integration safety**: PASS. The Windows contract requires one effective media
   owner, no duplicate commands, safe fallback, and local playback continuity.
4. **Local data integrity**: PASS. Helper binary integrity uses atomic replacement and
   broken/missing/repair-required states without user data migration.
5. **Responsiveness and verification**: PASS. Quickstart requires validation for explicit
   Next, natural EOF, helper interruption, local fallback, screen-reader feedback, and
   Windows media commands.

## Complexity Tracking

No constitution violations identified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
