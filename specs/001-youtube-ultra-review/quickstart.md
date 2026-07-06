# Quickstart: YouTube Ultra Review Planning Validation

## Prerequisites

- Windows development environment capable of running the application from source.
- Project dependencies installed according to `README.md`.
- YouTube helper components available or intentionally absent for failure-path checks.
- A network connection for YouTube search/link validation unless testing offline recovery.

## Validate Planning Artifacts

1. Confirm the feature spec exists at `specs/001-youtube-ultra-review/spec.md`.
2. Confirm this plan exists at `specs/001-youtube-ultra-review/plan.md`.
3. Confirm research decisions exist at `specs/001-youtube-ultra-review/research.md`.
4. Confirm the data model exists at `specs/001-youtube-ultra-review/data-model.md`.
5. Confirm the review output contract exists at
   `specs/001-youtube-ultra-review/contracts/review-output.md`.

Expected outcome: all artifacts are present and describe a current-state review, not an
implementation of fixes.

## Validate Review Scope Before Running the Review

Use the review output contract to verify the eventual review covers these flows:

1. Search for YouTube content.
2. Open a direct video link.
3. Open a playlist link.
4. Handle mixed video-plus-playlist links.
5. Browse results and return to results from playback.
6. Play current item and move to the next item.
7. Download the current YouTube item.
8. Install or update helper components.
9. Cancel active search, load, download, update, or preload work.
10. Recover from invalid links, no results, unavailable videos, and rate limits.

Expected outcome: each flow has a coverage status, validation evidence, and any findings
or missing validation clearly documented.

## Manual Validation Guidance for the Eventual Review

1. Run the application from the `player/` directory following `README.md`.
2. Verify keyboard/menu access for YouTube search, opening links, result navigation,
   playback, return-to-results, downloads, and cancellation.
3. Verify user feedback for success, progress, cancellation, and error paths.
4. Verify local file playback remains usable after YouTube failures.
5. Verify findings are written using the contract in `contracts/review-output.md`.

Expected outcome: maintainers can identify release blockers in under 5 minutes and every
critical/high finding includes evidence and validation guidance.
