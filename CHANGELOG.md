# سجل التغييرات (CHANGELOG)

- 2026-11-13: docs: rewrite the user guide and README in English and Arabic as matching mirrors verified against the code, and replace the two stale agent references with one PROJECT_REFERENCE.md.
- 2026-11-13: fix(i18n): review the whole Arabic catalog (meaning errors, calques, unified terms, restored menu accelerators, no fuzzy left) and add Arabic/Czech plural forms for the video age labels.
- 2026-11-13: refactor: remove dead dialogs (CustomSlider, old TaskDlg/BusyDlg/PlaylistDlg) and merge duplicated JSON store, key-map and byte-size helpers into helpers/.

- 2026-11-13: feat(youtube): add local YouTube subscriptions without a Google login: channels and playlists saved in subscriptions.json, latest videos from RSS (Ctrl+U), a management dialog (Ctrl+Shift+U), and subscribe from search results (Ctrl+S).

- 2026-11-13: feat(youtube): add a "Minutes to load ahead while playing" setting that caps mpv read-ahead with cache-secs, so switching videos early need not download the whole audio; 0, the default, keeps mpv's unlimited read-ahead.
- 2026-11-13: fix(youtube): make search language/region take effect (py_yt sent hl/gl outside context.client), validate the codes with a default fallback, and cancel queued prefetch jobs left behind when browsing results.
- 2026-11-13: chore(scripts): update_pot.py now merges and compiles every catalog, and update_version.py validates the version and runs the consistency check.
- 2026-11-13: feat(shell-open): add a General option to switch to the player when a file is opened from Explorer while it runs; off by default, so focus stays in Explorer.
- 2026-09-29: docs: caveman-compress PROJECT_REFERENCE.md (63,382 → 49,797 حرفاً؛ الأصل في `%LOCALAPPDATA%\caveman-compress\backups\simple-player\`).
- 2026-09-26: fix(youtube): restrict natural end-of-item auto-advancement to actual playlists respecting end_behavior and isolate stream playback from prior local playlist.
- 2026-09-26: fix(youtube): fix coroutine reuse crash upon re-entering search and unclosed httpx client in search runner.
