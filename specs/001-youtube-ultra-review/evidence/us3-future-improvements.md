# US3 Evidence: Future Improvements

- Evidence ID: EVID-US3-052
- Type: source-inspection
- Result: risk

## Future Improvements

- REC-016: Reuse strict host validation for current-source checks. Maps to YT-017.
- REC-017: Distinguish description failure from empty description. Maps to YT-018.
- REC-018: Improve result labels with channel/index metadata. Maps to YT-019.
- REC-019: Consolidate duplicate task/busy dialog implementations. Current source keeps YouTube-specific task/busy classes in `player/ui/yt_dialogs.py`, while current task code uses shared task dialogs through `player/youtube/task_ui.py` and `player/youtube/startup.py`.

## Classification

- These items are useful but should not block release unless manual validation uncovers user-facing breakage.
