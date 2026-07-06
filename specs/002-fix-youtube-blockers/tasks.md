---
description: "Task list for fixing YouTube release blockers"
---

# Tasks: Fix YouTube Release Blockers

**Input**: Design documents from `specs/002-fix-youtube-blockers/`

**Prerequisites**: `specs/002-fix-youtube-blockers/plan.md`, `specs/002-fix-youtube-blockers/spec.md`, `specs/002-fix-youtube-blockers/research.md`, `specs/002-fix-youtube-blockers/data-model.md`, `specs/002-fix-youtube-blockers/contracts/`, `specs/002-fix-youtube-blockers/quickstart.md`

**Validation**: Include automated tests for pure YouTube session/helper state when practical. Include explicit manual validation tasks for wxPython, MPV playback, helper interruption, screen-reader feedback, and Windows media controls.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on incomplete tasks
- **[Story]**: Maps task to the user story in `specs/002-fix-youtube-blockers/spec.md`
- Include exact file paths in descriptions

## Path Conventions

- **Application root**: `player/`
- **YouTube flow and helpers**: `player/youtube/`
- **Playback and Windows media**: `player/core/`, `player/core/player/`
- **Action routing**: `player/app_actions/`
- **Tests**: `tests/`
- **Validation evidence**: `specs/002-fix-youtube-blockers/validation-records.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish test and evidence structure for the release-blocker work.

- [X] T001 Create validation evidence skeleton with sections for YT-001 through YT-005 in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T002 Create test package directory and empty package marker in `tests/__init__.py`
- [X] T003 [P] Create YouTube test helpers skeleton for fake context, fake player, and fake sessions in `tests/helpers/youtube_fakes.py`
- [X] T004 [P] Create initial session continuity test file skeleton in `tests/test_youtube_session_continuity.py`
- [X] T005 [P] Create initial helper component integrity test file skeleton in `tests/test_youtube_component_integrity.py`
- [X] T006 [P] Create initial Windows media ownership test file skeleton in `tests/test_windows_media_ownership.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared state, cleanup, validation, and feedback primitives that block all release-blocker stories.

**CRITICAL**: No user story implementation should begin until this phase is complete.

- [X] T007 Document current YouTube session lifecycle entry points from `player/youtube/flow.py`, `player/youtube/results.py`, and `player/youtube/state.py` in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T008 Define reusable fake player source and queue behavior needed by session tests in `tests/helpers/youtube_fakes.py`
- [X] T009 Define reusable fake ActionContext behavior for `ctx.speak`, `ctx.player`, and YouTube session storage in `tests/helpers/youtube_fakes.py`
- [X] T010 Add validation record helper conventions for automated-check and manual-check entries in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T011 Add targeted session cleanup helper that can cancel a supplied session without clearing unrelated context session state in `player/youtube/state.py`
- [X] T012 Add helper readiness classification contract constants or functions for missing, ready, broken, and repair-required states in `player/youtube/components.py`
- [X] T013 Add one-owner Windows media decision note for custom bridge ownership in `specs/002-fix-youtube-blockers/validation-records.md`

**Checkpoint**: Foundation ready. Tests can create fake sessions/player state, validation evidence has a standard format, and shared cleanup/readiness concepts exist.

---

## Phase 3: User Story 1 - Preserve YouTube Playback Session Continuity (Priority: P1) MVP

**Goal**: Keep the correct YouTube session when browsing results, returning from playback, using explicit Next, and advancing at natural end-of-item.

**Independent Test**: Start playback from a YouTube search or playlist with at least three playable items, open and close another results view, return to the original results, use explicit Next, and let playback naturally advance without losing session state.

### Automated Validation for User Story 1

- [X] T014 [P] [US1] Add failing test for closing a secondary results session without clearing the active playback session in `tests/test_youtube_session_continuity.py`
- [X] T015 [P] [US1] Add failing test for targeted cleanup canceling only futures owned by the supplied session in `tests/test_youtube_session_continuity.py`
- [X] T016 [P] [US1] Add failing test for Escape removing session-owned player sources and clearing matching queued state in `tests/test_youtube_session_continuity.py`
- [X] T017 [P] [US1] Add failing test for explicit Next preparing the next item after return-to-results in `tests/test_youtube_session_continuity.py`
- [X] T018 [P] [US1] Add failing test for natural end-of-item invoking YouTube next handling for the active YouTube session in `tests/test_youtube_session_continuity.py`
- [X] T019 [P] [US1] Add failing test for unavailable next item producing spoken or visible feedback without clearing local playback state in `tests/test_youtube_session_continuity.py`

### Implementation for User Story 1

- [X] T020 [US1] Update results dialog close handling to call targeted cleanup for the displayed session in `player/youtube/results.py`
- [X] T021 [US1] Update result playback start to promote the displayed session to active playback ownership in `player/youtube/results.py`
- [X] T022 [US1] Update YouTube flow session creation and playback ownership transitions for search and playlist results in `player/youtube/flow.py`
- [X] T023 [US1] Update Escape return-to-results handling to invalidate queued state for removed YouTube sources in `player/youtube/flow.py`
- [X] T024 [US1] Add queue-state synchronization helper for removed source URLs in `player/youtube/state.py`
- [X] T025 [US1] Update `_ensure_queued` behavior to verify current player source state before trusting session queued state in `player/youtube/flow.py`
- [X] T026 [US1] Add active YouTube session next-item hook callable from playback completion in `player/youtube/flow.py`
- [X] T027 [US1] Integrate YouTube natural end-of-item hook into playback finished-file handling in `player/core/player/lifecycle.py`
- [X] T028 [US1] Route controller or player context needed by natural end-of-item YouTube advancement in `player/core/controller.py`
- [X] T029 [US1] Preserve existing explicit Next behavior while sharing next-preparation logic with natural end-of-item advancement in `player/youtube/flow.py`
- [X] T030 [US1] Add spoken or visible feedback for failed natural next-item preparation in `player/youtube/flow.py`
- [X] T031 [US1] Ensure local playback source handling is unchanged for non-YouTube EOF and explicit Next flows in `player/core/player/lifecycle.py`

### Manual Validation for User Story 1

- [X] T032 [US1] Record manual validation for YT-001 secondary results close preserving original session in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T033 [US1] Record manual validation for YT-002 Escape return-to-results followed by explicit Next in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T034 [US1] Record manual validation for YT-003 natural advancement through at least three YouTube items in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T035 [US1] Record manual validation for unavailable next item feedback and local playback fallback in `specs/002-fix-youtube-blockers/validation-records.md`

**Checkpoint**: User Story 1 is complete when YT-001, YT-002, and YT-003 have passing automated checks where practical and recorded manual playback validation.

---

## Phase 4: User Story 2 - Prevent Broken Helper Components From Appearing Ready (Priority: P1)

**Goal**: Ensure interrupted or failed helper setup cannot leave partial or unusable helper binaries reported as ready, while preserving local playback fallback.

**Independent Test**: Interrupt helper component setup during extraction or replacement, restart the application, verify YouTube helper readiness reports missing/broken/repair-required instead of ready, and confirm local media playback remains usable.

### Automated Validation for User Story 2

- [X] T036 [P] [US2] Add failing test for Deno partial file not being classified as ready in `tests/test_youtube_component_integrity.py`
- [X] T037 [P] [US2] Add failing test for atomic helper replacement preserving previous valid Deno on extraction failure in `tests/test_youtube_component_integrity.py`
- [X] T038 [P] [US2] Add failing test for canceled helper setup removing temporary files and reporting repair-required state in `tests/test_youtube_component_integrity.py`
- [X] T039 [P] [US2] Add failing test for missing or broken helpers producing recovery guidance text in `tests/test_youtube_component_integrity.py`

### Implementation for User Story 2

- [X] T040 [US2] Implement Deno readiness validation that distinguishes missing, ready, broken, and repair-required in `player/youtube/components.py`
- [X] T041 [US2] Implement yt-dlp readiness validation compatible with existing file-existence behavior in `player/youtube/components.py`
- [X] T042 [US2] Update `has_deno`, `has_yt`, and `has_all` to use readiness validation while preserving existing public behavior in `player/youtube/components.py`
- [X] T043 [US2] Replace direct Deno extraction to `deno.exe` with temporary-file extraction and atomic replace in `player/youtube/components.py`
- [X] T044 [US2] Add cleanup of Deno temporary files and partial targets on extraction failure or cancellation in `player/youtube/components.py`
- [X] T045 [US2] Update install-missing workflow to return clear non-ready state and recovery message after helper failure in `player/youtube/components.py`
- [X] T046 [US2] Update startup missing-component prompt to handle broken or repair-required helper states in `player/youtube/startup.py`
- [X] T047 [US2] Update YouTube search and link-open helper checks to surface visible or spoken recovery guidance for broken helpers in `player/youtube/flow.py`
- [X] T048 [US2] Ensure helper failure paths do not call local playback mutation or source removal behavior in `player/youtube/flow.py`

### Manual Validation for User Story 2

- [X] T049 [US2] Record manual validation for interrupted Deno extraction not reported as ready in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T050 [US2] Record manual validation for broken helper recovery guidance from a YouTube action in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T051 [US2] Record manual validation for local file playback after helper setup failure in `specs/002-fix-youtube-blockers/validation-records.md`

**Checkpoint**: User Story 2 is complete when YT-004 has passing helper integrity checks and manual validation for recovery guidance plus local playback fallback.

---

## Phase 5: User Story 3 - Ensure One Windows Media Control Owner (Priority: P2)

**Goal**: Ensure Windows media keys and system media controls are handled by one effective owner with safe fallback for local and YouTube playback.

**Independent Test**: Play local and YouTube media on Windows, use Play/Pause, Next, and Previous through system media controls, and verify each command triggers exactly one playback action and one coherent status display.

### Automated Validation for User Story 3

- [X] T052 [P] [US3] Add test or static assertion that MPV Windows media-control options are disabled when custom bridge ownership is selected in `tests/test_windows_media_ownership.py`
- [X] T053 [P] [US3] Add test for Windows media bridge unavailable fallback not raising during update or close in `tests/test_windows_media_ownership.py`
- [X] T054 [P] [US3] Add test for controller media command routing invoking one action per simulated bridge callback in `tests/test_windows_media_ownership.py`

### Implementation for User Story 3

- [X] T055 [US3] Disable MPV-owned Windows media controls and input media keys when custom bridge ownership is active in `player/core/mpv_engine.py`
- [X] T056 [US3] Document the custom bridge as the selected Windows media command/status owner in code comments near initialization in `player/core/controller.py`
- [X] T057 [US3] Verify WindowsMediaBridge remains guarded when `winsdk` is unavailable and close/update paths are safe in `player/core/windows_media.py`
- [X] T058 [US3] Ensure media bridge button callbacks route through existing controller action dispatch exactly once in `player/core/windows_media.py`
- [X] T059 [US3] Ensure controller shutdown still closes the custom Windows media bridge before MPV termination in `player/core/controller.py`
- [X] T060 [US3] Confirm YouTube playback metadata still reaches Windows media status through the selected owner in `player/core/controller.py`

### Manual Validation for User Story 3

- [X] T061 [US3] Record manual validation for local playback Play/Pause, Next, and Previous producing one action per Windows media command in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T062 [US3] Record manual validation for YouTube playback Play/Pause, Next, and Previous producing one action per Windows media command in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T063 [US3] Record manual validation for one coherent Windows media status with no duplicate sessions in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T064 [US3] Record manual validation for Windows media integration unavailable or disabled fallback preserving keyboard and local playback in `specs/002-fix-youtube-blockers/validation-records.md`

**Checkpoint**: User Story 3 is complete when YT-005 has one-owner behavior documented, automated checks where practical, and Windows manual validation recorded.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, regression checks, and documentation updates across all release blockers.

- [X] T065 [P] Run automated test suite for release-blocker tests and record command plus result in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T066 [P] Run quickstart planning artifact validation from `specs/002-fix-youtube-blockers/quickstart.md` and record result in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T067 [P] Verify keyboard/menu paths affected by YouTube search, open link, result browsing, return-to-results, and explicit Next in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T068 [P] Verify spoken or visible feedback for failed next item, broken helpers, and Windows fallback in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T069 Verify all five release blockers YT-001 through YT-005 have passing validation entries in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T070 Verify no medium or low YouTube review findings were included as unrelated scope in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T071 Run targeted local playback regression after YouTube failure scenarios and record result in `specs/002-fix-youtube-blockers/validation-records.md`
- [X] T072 Run final constitution compliance check for accessibility, MVC boundaries, Windows fallback, local data integrity, and responsiveness in `specs/002-fix-youtube-blockers/validation-records.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies and can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and is the MVP because it fixes core YouTube playback continuity blockers YT-001 through YT-003.
- **User Story 2 (Phase 4)**: Depends on Foundational and can run in parallel with User Story 1 after shared test/evidence helpers exist.
- **User Story 3 (Phase 5)**: Depends on Foundational and can run independently after Windows media ownership decision is documented.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other user stories after Phase 2.
- **User Story 2 (P1)**: No dependency on other user stories after Phase 2.
- **User Story 3 (P2)**: No dependency on User Story 1 or 2 for implementation, but final validation should include both local and YouTube playback.

### Within Each User Story

- Automated tests for pure state/helper behavior should be written before implementation tasks.
- Manual validation tasks should be completed after implementation tasks for that story.
- Tasks touching the same production file must be performed sequentially in listed order.
- Story checkpoints must pass before relying on that story in final polish.

---

## Parallel Opportunities

- T003 through T006 can run in parallel because they create separate test helper/test files.
- T014 through T019 can run in parallel after Phase 2 because they add independent tests in the same story test file but should be merged carefully.
- T036 through T039 can run in parallel because they cover independent helper integrity test cases.
- T052 through T054 can run in parallel because they cover independent Windows media ownership checks.
- US1 and US2 can be implemented in parallel after Phase 2 if file coordination prevents simultaneous edits to `player/youtube/flow.py`.
- T065 through T068 can run in parallel during final polish because they record distinct validation dimensions.

---

## Parallel Example: User Story 1

```bash
Task: "T014 [P] [US1] Add failing test for closing a secondary results session without clearing the active playback session in tests/test_youtube_session_continuity.py"
Task: "T016 [P] [US1] Add failing test for Escape removing session-owned player sources and clearing matching queued state in tests/test_youtube_session_continuity.py"
Task: "T018 [P] [US1] Add failing test for natural end-of-item invoking YouTube next handling for the active YouTube session in tests/test_youtube_session_continuity.py"
```

---

## Parallel Example: User Story 2

```bash
Task: "T036 [P] [US2] Add failing test for Deno partial file not being classified as ready in tests/test_youtube_component_integrity.py"
Task: "T037 [P] [US2] Add failing test for atomic helper replacement preserving previous valid Deno on extraction failure in tests/test_youtube_component_integrity.py"
Task: "T039 [P] [US2] Add failing test for missing or broken helpers producing recovery guidance text in tests/test_youtube_component_integrity.py"
```

---

## Parallel Example: User Story 3

```bash
Task: "T052 [P] [US3] Add test or static assertion that MPV Windows media-control options are disabled when custom bridge ownership is selected in tests/test_windows_media_ownership.py"
Task: "T053 [P] [US3] Add test for Windows media bridge unavailable fallback not raising during update or close in tests/test_windows_media_ownership.py"
Task: "T054 [P] [US3] Add test for controller media command routing invoking one action per simulated bridge callback in tests/test_windows_media_ownership.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate YT-001, YT-002, and YT-003 independently using automated checks and manual playback validation.
5. Use the MVP if the immediate release risk is YouTube playback continuity.

### Incremental Delivery

1. Complete Setup and Foundational work to establish fake test helpers, targeted cleanup, helper readiness classification, and validation record format.
2. Deliver User Story 1 to fix YouTube session continuity and next-track playback.
3. Deliver User Story 2 to fix helper component integrity and recovery.
4. Deliver User Story 3 to fix Windows media-control ownership.
5. Run Phase 6 to validate all five release blockers and constitution requirements.

### Parallel Team Strategy

1. One developer owns `player/youtube/flow.py` changes to avoid merge conflicts across US1 and US2.
2. One developer owns helper integrity in `player/youtube/components.py` and `player/youtube/startup.py`.
3. One developer owns Windows media behavior in `player/core/mpv_engine.py`, `player/core/controller.py`, and `player/core/windows_media.py`.
4. Validation evidence is consolidated in `specs/002-fix-youtube-blockers/validation-records.md` after each story checkpoint.

---

## Notes

- [P] tasks are parallelizable only when file coordination is handled; tasks touching the same file should still be merged sequentially.
- Automated tests are included because the plan explicitly calls for targeted checks for pure session/helper state where practical.
- Manual validation is required for wxPython UI, MPV playback, helper interruption, screen-reader behavior, and Windows media controls.
- Avoid implementing medium or low YouTube Ultra Review findings unless they are required to safely complete YT-001 through YT-005.
