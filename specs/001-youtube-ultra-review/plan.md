# Implementation Plan: YouTube Ultra Review

**Branch**: `main` | **Date**: 2026-07-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-youtube-ultra-review/spec.md`

## Summary

Perform a current-state ultra review of the existing YouTube feature. The review will
produce prioritized findings, journey coverage, validation evidence, and a remediation
sequence while explicitly excluding stale historical plans as authoritative evidence.

## Technical Context

**Language/Version**: Python 3.11 or newer recommended by project documentation

**Primary Dependencies**: wxPython desktop UI, libmpv playback, yt-dlp and Deno helper
components for YouTube workflows, py-yt-search for search behavior

**Storage**: Markdown planning and review artifacts under `specs/001-youtube-ultra-review/`;
no application data migration is planned for this review feature

**Testing**: Specification checklist, current-source inspection, targeted manual journey
validation, and optional automated checks for pure parsing/state behavior when available

**Target Platform**: Windows desktop application

**Project Type**: Desktop application review/audit feature

**Performance Goals**: Review covers at least eight YouTube journeys/support flows and
lets maintainers identify release blockers in under 5 minutes

**Constraints**: Use current source, current documentation, and observed behavior as
evidence; do not treat old review plans as authoritative; preserve keyboard-first and
screen-reader criteria; do not introduce code changes in this planning phase

**Scale/Scope**: Current YouTube workflow across search, link opening, playlist browsing,
playback, next-track behavior, downloads, component setup/update, cancellation, error
handling, and local playback fallback

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Accessibility and keyboard control**: PASS. The review scope explicitly requires
   keyboard/menu paths and spoken or visible feedback for all user-facing YouTube flows.
2. **Architecture boundaries**: PASS. The review will inspect current boundaries across
   YouTube workflow, action dispatch, playback, state, and UI behavior without proposing
   broad refactors as release blockers.
3. **Windows integration safety**: PASS. Component availability, bundled helpers,
   background work, and fallback to local playback are explicit review areas.
4. **Local data integrity**: PASS. This review does not mutate user data. It includes
   cleanup and stale session state as review risks where relevant.
5. **Responsiveness and verification**: PASS. The review requires validation for
   cancellation, background work, preloading, downloads, and user-facing recovery.

## Project Structure

### Documentation (this feature)

```text
specs/001-youtube-ultra-review/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── review-output.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
player/
├── youtube/                # Search, link resolution, results, sessions, downloads, components
├── app_actions/            # User-facing menu/hotkey action entry points
├── core/                   # Playback control, ActionContext, player state, Windows media integration
├── ui/                     # Dialogs, result lists, menus, and accessible UI behavior
├── config/                 # Settings, localization, constants, helper-component configuration
└── docs/ and locale/       # Help content and localized strings relevant to YouTube flows
```

**Structure Decision**: Review artifacts remain under the feature directory. Source
paths above define the review surface and evidence collection areas; no production code
changes are part of this planning phase.

## Phase 0: Research

Research output is captured in [research.md](./research.md). Decisions resolve the
review authority, scope boundaries, evidence standard, validation approach, and stale-plan
handling.

## Phase 1: Design & Contracts

Design artifacts:

- [data-model.md](./data-model.md): Review finding, scope item, validation evidence,
  and remediation recommendation entities.
- [contracts/review-output.md](./contracts/review-output.md): Required review report
  structure and acceptance contract.
- [quickstart.md](./quickstart.md): End-to-end guide for validating the review artifacts
  and running the eventual review.

Agent context update: skipped because this Spec Kit installation does not include an
agent-context update script under `.specify/scripts/`.

## Post-Design Constitution Check

1. **Accessibility and keyboard control**: PASS. Review output contract requires coverage
   of keyboard paths and spoken/visible feedback.
2. **Architecture boundaries**: PASS. Data model and contract separate findings, scope,
   evidence, and recommendations without prescribing implementation changes.
3. **Windows integration safety**: PASS. Contracts require component/setup/update and
   local playback fallback coverage.
4. **Local data integrity**: PASS. No data mutation is planned; cleanup/session-state
   risks are part of the review evidence model.
5. **Responsiveness and verification**: PASS. Quickstart requires cancellation,
   background-work, and preloading validation coverage.

## Complexity Tracking

No constitution violations identified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
