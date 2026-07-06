# Data Model: YouTube Ultra Review

## Review Finding

Represents one discovered defect, risk, missing validation item, or maintainability
concern.

**Fields**:

- `id`: Stable identifier such as `YT-001`.
- `severity`: One of `critical`, `high`, `medium`, `low`, or `info`.
- `category`: One of `confirmed-defect`, `risk`, `missing-validation`, or
  `maintenance-note`.
- `journey`: Related Review Scope Item identifier.
- `title`: Short finding title.
- `impact`: User-facing or maintainer-facing consequence.
- `evidence`: One or more Validation Evidence references.
- `recommendation`: Remediation Recommendation reference.
- `release_blocker`: Boolean value indicating whether the issue blocks release readiness.

**Validation rules**:

- Critical and high findings must include verification or reproduction guidance.
- Every finding must include at least one evidence reference.
- Every confirmed defect must include an affected user journey.

## Review Scope Item

Represents a YouTube journey or support flow included in the review.

**Fields**:

- `id`: Stable identifier such as `SCOPE-SEARCH`.
- `name`: Human-readable scope name.
- `priority`: `P1`, `P2`, or `P3`.
- `coverage_status`: One of `covered`, `partial`, `not-covered`, or `blocked`.
- `accessibility_expectation`: Keyboard path and spoken/visible feedback expected.
- `failure_expectation`: Expected recovery behavior when the flow fails.

**Validation rules**:

- The review must include at least eight scope items.
- Search, link opening, playlist browsing, playback, next-track behavior, downloads,
  component setup/update, and failure recovery are mandatory scope items.

## Validation Evidence

Represents evidence used to support a finding or confirm acceptable behavior.

**Fields**:

- `id`: Stable identifier such as `EVID-001`.
- `type`: One of `source-inspection`, `manual-check`, `automated-check`, or
  `documentation-reference`.
- `subject`: Journey, behavior, or artifact being evaluated.
- `result`: `pass`, `fail`, `risk`, or `not-run`.
- `details`: Concise observation or reproduction note.
- `limitations`: Any constraints or unverified assumptions.

**Validation rules**:

- Evidence must distinguish observed behavior from inferred risk.
- Evidence marked `not-run` cannot be the sole support for a confirmed defect.

## Remediation Recommendation

Represents the follow-up action proposed by the review.

**Fields**:

- `id`: Stable identifier such as `REC-001`.
- `priority`: One of `release-blocker`, `important-hardening`, or `future-improvement`.
- `action`: Plain-language recommended action.
- `expected_benefit`: User or maintainer benefit.
- `validation_needed`: Checks required before closure.

**Validation rules**:

- Release-blocker recommendations must map to critical or high findings.
- Future improvements must not be presented as required release work.

## Relationships

- One Review Scope Item can have many Review Findings.
- One Review Finding can reference many Validation Evidence entries.
- One Review Finding should map to one Remediation Recommendation.
- One Remediation Recommendation can address multiple related Review Findings.

## State Transitions

Review Finding lifecycle:

```text
identified -> evidenced -> prioritized -> accepted-for-remediation -> closed
identified -> evidenced -> deferred -> revisited
identified -> dismissed
```

Validation Evidence lifecycle:

```text
planned -> collected -> reviewed -> accepted
planned -> blocked
```
