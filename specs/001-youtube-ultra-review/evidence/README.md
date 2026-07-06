# Evidence Index

## Evidence ID Conventions

- `EVID-US1-NNN`: Source-inspection evidence for prioritized findings.
- `EVID-US2-NNN`: Journey validation evidence.
- `EVID-US3-NNN`: Remediation sequencing evidence.
- `EVID-POLISH-NNN`: Final contract, quickstart, constitution, and terminology checks.

## Entity Rules

Review Finding fields: `id`, `severity`, `category`, `journey`, `title`, `impact`, `evidence`, `recommendation`, `release_blocker`.

Review Scope Item fields: `id`, `name`, `priority`, `coverage_status`, `accessibility_expectation`, `failure_expectation`.

Validation Evidence fields: `id`, `type`, `subject`, `result`, `details`, `limitations`.

Remediation Recommendation fields: `id`, `priority`, `action`, `expected_benefit`, `validation_needed`.

## Validation Rules

- Critical and high findings include verification or reproduction guidance.
- Every finding includes at least one evidence reference.
- Every confirmed defect includes an affected user journey.
- Evidence distinguishes observed source behavior from inferred risk.
- Evidence marked `not-run` is not the sole support for a confirmed defect.
- Release-blocker recommendations map to critical or high findings.
- Future improvements are not presented as release blockers.

## Evidence Files

| File | Purpose |
|------|---------|
| `ui-accessibility-surface.md` | UI, menu, shortcut, and feedback surface map. |
| `playback-control-surface.md` | Playback, action context, MPV, and Windows media map. |
| `helper-settings-surface.md` | Helper component and YouTube settings map. |
| `manual-validation-environment.md` | Manual validation assumptions and limitations. |
| `us1-*.md` | Finding-oriented source inspection evidence. |
| `us2-*.md` | Journey validation evidence. |
| `us3-*.md` | Remediation sequencing supporting notes. |
| `quickstart-validation.md` | Planning artifact validation. |
| `report-terminology-review.md` | Data-model terminology validation. |
| `constitution-*.md` | Constitution compliance checks. |
