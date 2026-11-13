# سجل التغييرات (CHANGELOG)

- 2026-11-13: chore(mpv): upgrade libmpv to 0.42 (shinchiro 20261111) and python-mpv to 1.0.8 with one loader patch, adapting end-file reasons, the duration probe and volume-max; on branch mpv-update until Kamal tests it live.

- 2026-11-13: fix(silence): put silence removal first in the mpv filter chain (af pre), because dynaudnorm, on by default, lifted the background noise of pauses above the threshold so nothing was trimmed; and refuse a threshold of 0 dB or more, which muted all audio.

- 2026-11-13: test: Kamal confirmed live with NVDA the subscriptions, the reviewed Arabic UI, the 2026-11-13 fixes, the new Arabic installer and the in-app update from 1.5.0 to 2.0.0.

- 2026-11-13: release: 2.0.0 (subscriptions, Arabic review, new bilingual guide, installer fixes), with bilingual update notes in info.json and both What's New pages.

- 2026-11-13: build(installer): stop forcing default file associations (they broke after uninstall), add Arabic and Czech setup languages, remove runtime yt-dlp/deno on uninstall, drop the Start-menu page, fail when Updater.exe is missing, pin Inno Setup 6.7.3 in release.yml, and let build_test.ps1 use an active venv.

- 2026-11-13: fix: Reset settings refreshes the other Preferences pages, global shortcuts accept Home/End/Delete/Backspace, a video opened in folder mode stays in the list and plays first, seek-step labels and the YouTube components prompt are translated, and Backup and restore can export/import favorites and subscriptions.

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
