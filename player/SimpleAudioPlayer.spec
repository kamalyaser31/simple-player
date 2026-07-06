# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs


PROJECT_ROOT = Path.cwd()

binaries = []
binaries += collect_dynamic_libs("accessible_output3")
binaries += [
    (str(PROJECT_ROOT / "mpv.dll"), "."),
]

datas = []
datas += collect_data_files("accessible_output3")
datas += collect_data_files("certifi")
datas += [
    (str(PROJECT_ROOT / "sounds" / "speaker_test.wav"), "sounds"),
]
locale_root = PROJECT_ROOT / "locale"
if locale_root.exists():
    for path in locale_root.rglob("*"):
        if not path.is_file():
            continue
        rel_parent = path.relative_to(locale_root).parent
        dest = Path("locale") / rel_parent
        datas.append((str(path), str(dest)))
docs_root = PROJECT_ROOT / "docs"
if docs_root.exists():
    for path in docs_root.rglob("*"):
        if not path.is_file():
            continue
        rel_parent = path.relative_to(docs_root).parent
        dest = Path("docs") / rel_parent
        datas.append((str(path), str(dest)))
updater_exe = PROJECT_ROOT / "Updater.exe"
if updater_exe.exists():
    datas += [(str(updater_exe), ".")]

a = Analysis(
    ["SimpleAudioPlayer.py"],
    pathex=[str(PROJECT_ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        "winsdk.windows.media",
        "winsdk.windows.media.playback",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SimpleAudioPlayer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory=".",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="SimpleAudioPlayer",
)
