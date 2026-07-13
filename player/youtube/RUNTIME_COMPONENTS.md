# YouTube runtime components

Release packages do not bundle `yt-dlp.exe` or `deno.exe`. The application
installs both components into its application directory on first use and keeps
yt-dlp current through the selected update channel. Local developer copies are
ignored build inputs and must never be added to `SimpleAudioPlayer.spec`.

This runtime-installed policy is checked by
`scripts/validate_project_consistency.py`. A future bundled policy must update
the installer, PyInstaller spec, component installer, and this validation in
one change.
