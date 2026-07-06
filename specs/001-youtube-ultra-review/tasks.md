---
description: "Task list for YouTube Ultra Review"
---

# Tasks: YouTube Ultra Review

**Input**: Design documents from `specs/001-youtube-ultra-review/`

**Prerequisites**: `specs/001-youtube-ultra-review/plan.md`, `specs/001-youtube-ultra-review/spec.md`, `specs/001-youtube-ultra-review/research.md`, `specs/001-youtube-ultra-review/data-model.md`, `specs/001-youtube-ultra-review/contracts/review-output.md`, `specs/001-youtube-ultra-review/quickstart.md`

**Validation**: This feature produces a review/audit artifact, not production code. Validation tasks focus on current-source inspection, targeted manual journey checks, report-contract compliance, and explicit evidence capture.

**Organization**: Tasks are grouped by user story so each story can be completed and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it creates or edits different files and does not depend on incomplete tasks
- **[Story]**: Maps task to the user story in `specs/001-youtube-ultra-review/spec.md`
- **File paths**: Every task includes exact paths for the artifact or source files involved

## Path Conventions

- **Review artifacts**: `specs/001-youtube-ultra-review/`
- **Source review surface**: `player/youtube/`, `player/app_actions/`, `player/core/`, `player/ui/`, `player/config/`
- **Final report**: `specs/001-youtube-ultra-review/youtube-ultra-review.md`
- **Evidence files**: `specs/001-youtube-ultra-review/evidence/`

---

## Phase 1: Setup (Shared Review Infrastructure)

**Purpose**: Create the review artifact skeletons and evidence structure before source or journey work begins.

- [X] T001 Create final report skeleton with contract sections from `specs/001-youtube-ultra-review/contracts/review-output.md` in `specs/001-youtube-ultra-review/youtube-ultra-review.md`
- [X] T002 Create evidence index with evidence ID conventions `EVID-001` through `EVID-NNN` in `specs/001-youtube-ultra-review/evidence/README.md`
- [X] T003 [P] Create journey coverage matrix skeleton with mandatory scope items from `specs/001-youtube-ultra-review/data-model.md` in `specs/001-youtube-ultra-review/validation-matrix.md`
- [X] T004 [P] Create source review map skeleton covering `player/youtube/`, `player/app_actions/`, `player/core/`, `player/ui/`, and `player/config/` in `specs/001-youtube-ultra-review/source-map.md`
- [X] T005 [P] Create remediation sequence skeleton with release-blocker, important-hardening, and future-improvement sections in `specs/001-youtube-ultra-review/remediation-sequence.md`
- [X] T006 Record the stale historical plan exclusion rule from `specs/001-youtube-ultra-review/research.md` in `specs/001-youtube-ultra-review/source-map.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the review rules, current-source boundary, and evidence taxonomy that every user story depends on.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T007 Extract report acceptance rules from `specs/001-youtube-ultra-review/contracts/review-output.md` into `specs/001-youtube-ultra-review/youtube-ultra-review.md`
- [X] T008 Extract review entities and validation rules from `specs/001-youtube-ultra-review/data-model.md` into `specs/001-youtube-ultra-review/evidence/README.md`
- [X] T009 Map current YouTube modules `player/youtube/actions.py`, `player/youtube/flow.py`, `player/youtube/search.py`, `player/youtube/resolver.py`, `player/youtube/results.py`, `player/youtube/state.py`, and `player/youtube/download.py` in `specs/001-youtube-ultra-review/source-map.md`
- [X] T010 [P] Map UI and accessibility review surface `player/ui/yt_dialogs.py`, `player/ui/task_dialogs.py`, `player/ui/main_frame.py`, and `player/speech.py` in `specs/001-youtube-ultra-review/evidence/ui-accessibility-surface.md`
- [X] T011 [P] Map playback and control review surface `player/core/controller.py`, `player/core/action_context.py`, `player/core/player/`, and `player/core/windows_media.py` in `specs/001-youtube-ultra-review/evidence/playback-control-surface.md`
- [X] T012 [P] Map helper component and settings review surface `player/youtube/components.py`, `player/youtube/startup.py`, `player/config/constants.py`, and `player/ui/prefs/youtube.py` in `specs/001-youtube-ultra-review/evidence/helper-settings-surface.md`
- [X] T013 Define severity categories, finding categories, release-blocker criteria, and evidence limitations in `specs/001-youtube-ultra-review/youtube-ultra-review.md`
- [X] T014 Define manual validation environment assumptions from `specs/001-youtube-ultra-review/quickstart.md` in `specs/001-youtube-ultra-review/evidence/manual-validation-environment.md`

**Checkpoint**: Foundation ready. Current-source scope, evidence format, and report acceptance rules are documented.

---

## Phase 3: User Story 1 - Receive Current-State Review Findings (Priority: P1) MVP

**Goal**: Produce prioritized current-state findings with severity, evidence, user impact, affected behavior, validation guidance, and next action.

**Independent Test**: A maintainer can read `specs/001-youtube-ultra-review/youtube-ultra-review.md` and see findings grouped by severity with evidence, impact, affected journey, and recommended next action.

### Validation for User Story 1

- [X] T015 [US1] Define finding completeness checklist for `specs/001-youtube-ultra-review/youtube-ultra-review.md` covering finding ID, severity, category, affected journey, impact, evidence, verification guidance, recommended next action, and release-blocker status
- [X] T016 [US1] Define stale-authority exclusion checklist for `specs/001-youtube-ultra-review/youtube-ultra-review.md` so findings cannot rely solely on historical plans
- [X] T017 [US1] Define critical and high finding verification checklist for `specs/001-youtube-ultra-review/youtube-ultra-review.md` covering reproduction or verification guidance

### Implementation for User Story 1

- [X] T018 [P] [US1] Inspect YouTube action entry points in `player/youtube/actions.py` and record current behavior evidence in `specs/001-youtube-ultra-review/evidence/us1-actions-entrypoints.md`
- [X] T019 [P] [US1] Inspect YouTube flow orchestration in `player/youtube/flow.py` and record state transition evidence in `specs/001-youtube-ultra-review/evidence/us1-flow-orchestration.md`
- [X] T020 [P] [US1] Inspect search implementation in `player/youtube/search.py` and record search reliability evidence in `specs/001-youtube-ultra-review/evidence/us1-search.md`
- [X] T021 [P] [US1] Inspect link validation and stream resolution in `player/youtube/link_validator.py`, `player/youtube/resolver.py`, and `player/youtube/video.py` in `specs/001-youtube-ultra-review/evidence/us1-link-resolution.md`
- [X] T022 [P] [US1] Inspect playlist result state in `player/youtube/results.py` and `player/youtube/state.py` in `specs/001-youtube-ultra-review/evidence/us1-results-state.md`
- [X] T023 [P] [US1] Inspect download behavior in `player/youtube/download.py` and record failure, cancellation, and user-feedback evidence in `specs/001-youtube-ultra-review/evidence/us1-downloads.md`
- [X] T024 [P] [US1] Inspect helper component behavior in `player/youtube/components.py` and `player/youtube/startup.py` in `specs/001-youtube-ultra-review/evidence/us1-helper-components.md`
- [X] T025 [P] [US1] Inspect accessible feedback and dialogs in `player/ui/yt_dialogs.py`, `player/youtube/task_ui.py`, `player/youtube/ui_utils.py`, and `player/speech.py` in `specs/001-youtube-ultra-review/evidence/us1-accessibility-feedback.md`
- [X] T026 [P] [US1] Inspect playback fallback interactions in `player/core/controller.py`, `player/core/player/`, and `player/core/windows_media.py` in `specs/001-youtube-ultra-review/evidence/us1-playback-fallback.md`
- [X] T027 [US1] Consolidate evidence from `specs/001-youtube-ultra-review/evidence/us1-*.md` into prioritized findings in `specs/001-youtube-ultra-review/youtube-ultra-review.md`
- [X] T028 [US1] Add executive summary finding counts by severity and release-blocker status to `specs/001-youtube-ultra-review/youtube-ultra-review.md`
- [X] T029 [US1] Cross-check User Story 1 acceptance scenarios from `specs/001-youtube-ultra-review/spec.md` against `specs/001-youtube-ultra-review/youtube-ultra-review.md`

**Checkpoint**: User Story 1 is complete when the final report contains actionable current-state findings that meet the output contract.

---

## Phase 4: User Story 2 - Validate Core YouTube User Journeys (Priority: P2)

**Goal**: Cover YouTube search, link opening, playlist browsing, stream playback, next-track behavior, downloads, component setup/update, cancellation, failure recovery, accessibility feedback, and local playback fallback.

**Independent Test**: The review lists each covered journey in `specs/001-youtube-ultra-review/validation-matrix.md` and identifies whether the journey is covered, partially covered, blocked, or missing validation.

### Validation for User Story 2

- [X] T030 [US2] Define journey coverage checklist for `specs/001-youtube-ultra-review/validation-matrix.md` covering search, direct link opening, playlist browsing, stream playback, next-track behavior, downloads, component setup/update, cancellation and failure recovery, accessibility feedback, and local playback fallback
- [X] T031 [US2] Define journey row completeness checklist for `specs/001-youtube-ultra-review/validation-matrix.md` covering coverage status, accessibility expectation, failure expectation, evidence reference, and linked finding ID
- [X] T032 [US2] Define user-facing failure checklist for `specs/001-youtube-ultra-review/validation-matrix.md` covering expected spoken or visible feedback and recovery behavior

### Implementation for User Story 2

- [X] T033 [P] [US2] Validate YouTube search journey covering result discovery, first playable result, cancellation, error messaging, and accessibility feedback in `specs/001-youtube-ultra-review/evidence/us2-search-journey.md`
- [X] T034 [P] [US2] Validate direct video link journey covering valid links, invalid links, unsupported links, removed videos, and recovery behavior in `specs/001-youtube-ultra-review/evidence/us2-direct-link-journey.md`
- [X] T035 [P] [US2] Validate playlist link and mixed video-plus-playlist journey covering playlist detection, item availability, and result population in `specs/001-youtube-ultra-review/evidence/us2-playlist-link-journey.md`
- [X] T036 [P] [US2] Validate playlist browsing and return-to-results journey covering keyboard navigation, selected item playback, and session cleanup in `specs/001-youtube-ultra-review/evidence/us2-playlist-browsing-journey.md`
- [X] T037 [P] [US2] Validate stream playback journey covering resolution handoff, MPV playback start, progress feedback, and local playback fallback in `specs/001-youtube-ultra-review/evidence/us2-stream-playback-journey.md`
- [X] T038 [P] [US2] Validate next-track and preloading journey covering successful advance, failed preload, unavailable next item, and leaving session before resolution completes in `specs/001-youtube-ultra-review/evidence/us2-next-track-preload-journey.md`
- [X] T039 [P] [US2] Validate download journey covering current item download, cancellation, output feedback, and failure recovery in `specs/001-youtube-ultra-review/evidence/us2-download-journey.md`
- [X] T040 [P] [US2] Validate helper component setup and update journey covering missing, outdated, blocked, and failed helper components in `specs/001-youtube-ultra-review/evidence/us2-helper-component-journey.md`
- [X] T041 [P] [US2] Validate cancellation and background-work recovery across search, stream loading, download, update, and preload flows in `specs/001-youtube-ultra-review/evidence/us2-cancellation-recovery-journey.md`
- [X] T042 [P] [US2] Validate accessibility feedback journey covering keyboard path, menu path, spoken feedback, visible dialogs, duplicate feedback, and silent failures in `specs/001-youtube-ultra-review/evidence/us2-accessibility-journey.md`
- [X] T043 [P] [US2] Validate local playback fallback after YouTube failures using `player/core/controller.py` and current application behavior in `specs/001-youtube-ultra-review/evidence/us2-local-playback-fallback.md`
- [X] T044 [US2] Consolidate journey evidence from `specs/001-youtube-ultra-review/evidence/us2-*.md` into `specs/001-youtube-ultra-review/validation-matrix.md`
- [X] T045 [US2] Add missing validation, blocked checks, environment limitations, and not-run evidence from `specs/001-youtube-ultra-review/evidence/us2-*.md` to `specs/001-youtube-ultra-review/youtube-ultra-review.md`
- [X] T046 [US2] Cross-check User Story 2 acceptance scenarios and edge cases from `specs/001-youtube-ultra-review/spec.md` against `specs/001-youtube-ultra-review/validation-matrix.md`

**Checkpoint**: User Story 2 is complete when every required journey has coverage status, validation evidence, and documented recovery or feedback expectations.

---

## Phase 5: User Story 3 - Produce a Prioritized Remediation Path (Priority: P3)

**Goal**: Separate release blockers, important hardening, and future improvements so follow-up work can be planned without mixing urgent bugs with optional refactors.

**Independent Test**: The final review includes a remediation summary that maps each issue to priority, validation need, and release-readiness impact.

### Validation for User Story 3

- [X] T047 [US3] Define remediation ordering checklist for `specs/001-youtube-ultra-review/remediation-sequence.md` so release blockers appear before important hardening and future improvements
- [X] T048 [US3] Define release-blocker mapping checklist for `specs/001-youtube-ultra-review/remediation-sequence.md` against critical and high findings in `specs/001-youtube-ultra-review/youtube-ultra-review.md`
- [X] T049 [US3] Define future-improvement classification checklist for `specs/001-youtube-ultra-review/remediation-sequence.md` so optional work is not described as required release work

### Implementation for User Story 3

- [X] T050 [P] [US3] Draft release-blocker recommendations from critical and high findings in `specs/001-youtube-ultra-review/remediation-sequence.md`
- [X] T051 [P] [US3] Draft important-hardening recommendations from medium-risk findings and missing validation in `specs/001-youtube-ultra-review/evidence/us3-important-hardening.md`
- [X] T052 [P] [US3] Draft future-improvement recommendations from maintenance notes and low-risk findings in `specs/001-youtube-ultra-review/evidence/us3-future-improvements.md`
- [X] T053 [US3] Consolidate `specs/001-youtube-ultra-review/evidence/us3-important-hardening.md` and `specs/001-youtube-ultra-review/evidence/us3-future-improvements.md` into `specs/001-youtube-ultra-review/remediation-sequence.md`
- [X] T054 [US3] Add validation-needed details for each remediation recommendation in `specs/001-youtube-ultra-review/remediation-sequence.md`
- [X] T055 [US3] Copy the final remediation sequence from `specs/001-youtube-ultra-review/remediation-sequence.md` into `specs/001-youtube-ultra-review/youtube-ultra-review.md`
- [X] T056 [US3] Cross-check User Story 3 acceptance scenarios from `specs/001-youtube-ultra-review/spec.md` against `specs/001-youtube-ultra-review/remediation-sequence.md`

**Checkpoint**: User Story 3 is complete when maintainers can identify release blockers in under 5 minutes and distinguish urgent fixes from hardening and future work.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, contract compliance, and readability checks across all review artifacts.

- [X] T057 [P] Run quickstart planning artifact validation from `specs/001-youtube-ultra-review/quickstart.md` and record results in `specs/001-youtube-ultra-review/evidence/quickstart-validation.md`
- [X] T058 [P] Verify final report terminology against `specs/001-youtube-ultra-review/data-model.md` and record corrections in `specs/001-youtube-ultra-review/evidence/report-terminology-review.md`
- [X] T059 [P] Verify accessibility and keyboard-control coverage against `.specify/memory/constitution.md` and record results in `specs/001-youtube-ultra-review/evidence/constitution-accessibility-review.md`
- [X] T060 [P] Verify responsiveness, cancellation, and background-work coverage against `.specify/memory/constitution.md` and record results in `specs/001-youtube-ultra-review/evidence/constitution-responsiveness-review.md`
- [X] T061 Verify every evidence reference used in `specs/001-youtube-ultra-review/youtube-ultra-review.md` points to an existing file under `specs/001-youtube-ultra-review/evidence/`
- [X] T062 Verify `specs/001-youtube-ultra-review/youtube-ultra-review.md` includes all required sections from `specs/001-youtube-ultra-review/contracts/review-output.md`
- [X] T063 Verify `specs/001-youtube-ultra-review/validation-matrix.md` covers all flows listed in `specs/001-youtube-ultra-review/quickstart.md`
- [X] T064 Verify final review readability by checking that release blockers are identifiable within 5 minutes in `specs/001-youtube-ultra-review/youtube-ultra-review.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies and can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion and provides the MVP findings report.
- **User Story 2 (Phase 4)**: Depends on Foundational completion and can run alongside User Story 1 after shared evidence conventions exist.
- **User Story 3 (Phase 5)**: Depends on at least the User Story 1 findings and reaches full value after User Story 2 journey coverage is complete.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2. No dependency on other stories.
- **User Story 2 (P2)**: Can start after Phase 2. It is independently testable through `specs/001-youtube-ultra-review/validation-matrix.md`.
- **User Story 3 (P3)**: Can start after Phase 3 because remediation sequencing depends on findings. It should be finalized after Phase 4 so missing validation and journey risks are included.

### Within Each User Story

- Validation tasks define the acceptance gate before consolidating the story output.
- Source or journey evidence files are collected before consolidation tasks.
- Consolidation tasks update the final report or matrix after individual evidence tasks finish.
- Cross-check tasks close each story against `specs/001-youtube-ultra-review/spec.md`.

---

## Parallel Opportunities

- T003, T004, and T005 can run in parallel after T001 and T002 because they create separate artifact files.
- T010, T011, and T012 can run in parallel because they create separate evidence files.
- T018 through T026 can run in parallel because each task writes to a distinct `specs/001-youtube-ultra-review/evidence/us1-*.md` file.
- T033 through T043 can run in parallel because each task writes to a distinct `specs/001-youtube-ultra-review/evidence/us2-*.md` file.
- T050, T051, and T052 can run in parallel if User Story 1 findings have already been drafted.
- T057, T058, T059, and T060 can run in parallel during final polish because they write distinct evidence files.

---

## Parallel Example: User Story 1

```bash
Task: "T018 [P] [US1] Inspect YouTube action entry points in player/youtube/actions.py and record current behavior evidence in specs/001-youtube-ultra-review/evidence/us1-actions-entrypoints.md"
Task: "T020 [P] [US1] Inspect search implementation in player/youtube/search.py and record search reliability evidence in specs/001-youtube-ultra-review/evidence/us1-search.md"
Task: "T024 [P] [US1] Inspect helper component behavior in player/youtube/components.py and player/youtube/startup.py in specs/001-youtube-ultra-review/evidence/us1-helper-components.md"
Task: "T026 [P] [US1] Inspect playback fallback interactions in player/core/controller.py, player/core/player/, and player/core/windows_media.py in specs/001-youtube-ultra-review/evidence/us1-playback-fallback.md"
```

---

## Parallel Example: User Story 2

```bash
Task: "T033 [P] [US2] Validate YouTube search journey in specs/001-youtube-ultra-review/evidence/us2-search-journey.md"
Task: "T035 [P] [US2] Validate playlist link and mixed video-plus-playlist journey in specs/001-youtube-ultra-review/evidence/us2-playlist-link-journey.md"
Task: "T038 [P] [US2] Validate next-track and preloading journey in specs/001-youtube-ultra-review/evidence/us2-next-track-preload-journey.md"
Task: "T040 [P] [US2] Validate helper component setup and update journey in specs/001-youtube-ultra-review/evidence/us2-helper-component-journey.md"
```

---

## Parallel Example: User Story 3

```bash
Task: "T050 [P] [US3] Draft release-blocker recommendations from critical and high findings in specs/001-youtube-ultra-review/remediation-sequence.md"
Task: "T051 [P] [US3] Draft important-hardening recommendations in specs/001-youtube-ultra-review/evidence/us3-important-hardening.md"
Task: "T052 [P] [US3] Draft future-improvement recommendations in specs/001-youtube-ultra-review/evidence/us3-future-improvements.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate User Story 1 independently using T015, T016, T017, and T029.
5. Use `specs/001-youtube-ultra-review/youtube-ultra-review.md` as the MVP review output if immediate maintainer feedback is needed.

### Incremental Delivery

1. Complete Setup and Foundational work to establish report contract, evidence conventions, and current-source boundaries.
2. Deliver User Story 1 to produce actionable current-state findings.
3. Deliver User Story 2 to add journey coverage and validation completeness.
4. Deliver User Story 3 to sequence remediation into release blockers, important hardening, and future improvements.
5. Run Phase 6 to ensure the final report is contract-compliant and easy to consume.

### Parallel Team Strategy

1. One reviewer owns final report consistency in `specs/001-youtube-ultra-review/youtube-ultra-review.md`.
2. Multiple reviewers collect source and journey evidence in separate files under `specs/001-youtube-ultra-review/evidence/`.
3. One reviewer consolidates `specs/001-youtube-ultra-review/validation-matrix.md` after journey evidence is complete.
4. One reviewer consolidates `specs/001-youtube-ultra-review/remediation-sequence.md` after findings are prioritized.

---

## Notes

- [P] tasks write to different files or can be completed without depending on incomplete tasks.
- No production code changes are part of this task list unless a later feature explicitly turns findings into implementation work.
- Manual validation is acceptable for wxPython, MPV, helper components, screen-reader feedback, and Windows-specific behavior.
- Evidence must distinguish confirmed behavior from inferred risk and must document limitations when checks cannot be run.
