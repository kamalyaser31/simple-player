# Contract: YouTube Ultra Review Output

The final review report must follow this structure so findings are actionable and easy
to convert into implementation tasks.

## Required Sections

1. **Executive Summary**
   - Overall readiness assessment.
   - Count of findings by severity.
   - Release-blocker summary, if any.

2. **Journey Coverage Matrix**
   - Search.
   - Direct link opening.
   - Playlist browsing.
   - Stream playback.
   - Next-track behavior.
   - Downloads.
   - Component setup/update.
   - Cancellation and failure recovery.
   - Accessibility feedback.
   - Local playback fallback.

3. **Findings**
   - Ordered by severity, then user impact.
   - Each finding must include:
     - Finding ID.
     - Severity.
     - Category.
     - Affected journey.
     - Impact.
     - Evidence.
     - Reproduction or verification guidance.
     - Recommended next action.
     - Release-blocker status.

4. **Missing Validation**
   - Manual checks not yet run.
   - Automated checks not yet available.
   - Environment limitations.

5. **Remediation Sequence**
   - Release blockers.
   - Important hardening.
   - Future improvements.

## Acceptance Rules

- The report must not use stale historical plans as standalone evidence.
- Critical and high findings must include verification guidance.
- Every user-facing failure finding must describe expected user recovery.
- Every accessibility finding must describe keyboard path or spoken/visible feedback impact.
- Every platform or helper-component finding must describe whether local playback remains usable.
