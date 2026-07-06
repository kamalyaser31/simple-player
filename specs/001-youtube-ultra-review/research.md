# Research: YouTube Ultra Review

## Decision: Treat Current Behavior as the Only Review Authority

**Rationale**: The user stated that the existing ultra review plan is very old. The
review must therefore rely on current source, current documentation, and observable
behavior.

**Alternatives considered**: Reuse the old review plan as a roadmap. Rejected because it
can misrepresent current risks and create stale priorities.

## Decision: Scope the Review Around User Journeys First

**Rationale**: The YouTube feature is user-facing and spans search, link opening,
playlist browsing, playback, next-track behavior, downloads, component setup/update,
cancellation, and recovery. Journey-first review keeps findings tied to user impact.

**Alternatives considered**: Review files alphabetically. Rejected because it can produce
low-value maintainability notes while missing cross-flow playback or accessibility bugs.

## Decision: Separate Confirmed Defects, Risks, Missing Validation, and Maintenance Notes

**Rationale**: The final review needs to help maintainers identify release blockers
quickly without mixing urgent failures with optional cleanups.

**Alternatives considered**: Use one flat findings list. Rejected because severity and
actionability become unclear for a broad review.

## Decision: Use Manual Validation for GUI, Playback, Screen-Reader, and Windows-Specific Behavior

**Rationale**: The project depends on desktop UI, media playback, helper binaries,
background work, and platform behavior that are expensive or unreliable to automate in
this planning phase. Manual validation is acceptable where automation is impractical.

**Alternatives considered**: Require full automated coverage before review completion.
Rejected because it would block useful review output and exceed the scope of an audit
feature.

## Decision: Prefer Automated Checks for Pure Parsing and State Behavior When Available

**Rationale**: Link parsing, state transitions, and report-shape validation can be
checked more repeatably than full GUI/playback flows.

**Alternatives considered**: Manual-only validation. Rejected because pure behavior can
often be verified faster and with less ambiguity through automated checks.

## Decision: Contract the Review Output Format

**Rationale**: A review is only useful if each finding has severity, evidence, impact,
validation, and next action. A contract prevents vague or non-actionable output.

**Alternatives considered**: Free-form review notes. Rejected because they may omit
critical metadata needed for planning follow-up fixes.
