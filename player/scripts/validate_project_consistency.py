import ast
import json
import re
import sys
from pathlib import Path


def validate_project(player_root=None):
    player = Path(player_root or Path(__file__).resolve().parents[1])
    repository = player.parent
    errors = []
    constants = _assignments(player / "config" / "constants.py")
    associations = _assignments(player / "config" / "file_associations.py")
    dialogs = _assignments(player / "ui" / "dialogs.py")
    installer = (player / "simple_audio_player.iss").read_text(encoding="utf-8")
    spec = (player / "SimpleAudioPlayer.spec").read_text(encoding="utf-8")

    _check_versions(repository, constants, installer, errors)
    _check_associations(constants, associations, dialogs, installer, errors)
    _check_catalogs(player, constants, errors)
    _check_packaging(player, repository, spec, errors)
    _check_updater(constants, installer, errors)
    _check_release_names(repository, constants, errors)
    _check_runtime_policy(player, spec, errors)
    return errors


def _assignments(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        try:
            values[target.id] = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            continue
    return values


def _check_versions(repository, constants, installer, errors):
    published = json.loads((repository / "info.json").read_text(encoding="utf-8"))
    match = re.search(r'#define\s+MyAppVersion\s+"([^"]+)"', installer)
    versions = {
        str(published.get("version") or ""),
        str(constants.get("APP_VERSION") or ""),
        match.group(1) if match else "",
    }
    if len(versions) != 1 or "" in versions:
        errors.append("Version mismatch: info.json, APP_VERSION, and MyAppVersion.")


def _check_associations(constants, associations, dialogs, installer, errors):
    audio_extensions = set(constants.get("AUDIO_EXTENSIONS", set()))
    python_extensions = audio_extensions | set(
        associations.get("VIDEO_EXTENSIONS", set())
    )
    wildcard = str(dialogs.get("AUDIO_WILDCARD") or "")
    wildcard_extensions = {
        f".{ext}" for ext in re.findall(r"\*\.([a-z0-9]+)", wildcard)
    }
    if audio_extensions != wildcard_extensions:
        errors.append("Audio extensions differ between constants and the file dialog.")
    for name, pattern in _INSTALLER_EXTENSION_PATTERNS.items():
        if python_extensions != set(re.findall(pattern, installer)):
            errors.append(f"File association extensions differ in Inno {name} entries.")


_INSTALLER_EXTENSION_PATTERNS = {
    "SupportedTypes": r'SupportedTypes";\s+ValueType: string;\s+ValueName: "(\.[^"]+)"',
    "OpenWithProgids": r'Subkey: "Software\\Classes\\(\.[^"\\]+)\\OpenWithProgids"',
    "capabilities": r'Capabilities\\FileAssociations";\s+ValueType: string;\s+ValueName: "(\.[^"]+)"',
}


def _check_catalogs(player, constants, errors):
    domain = str(constants.get("DOMAIN") or "")
    for language in (player / "locale").iterdir():
        messages = language / "LC_MESSAGES"
        if not messages.is_dir():
            continue
        if not (messages / f"{domain}.mo").is_file():
            errors.append(
                f"Missing runtime catalog: {language.name}/LC_MESSAGES/{domain}.mo"
            )
        po_files = list(messages.glob("*.po"))
        if po_files and not (messages / f"{domain}.po").is_file():
            errors.append(f"Catalog source has wrong domain name: {language.name}.")


def _check_packaging(player, repository, spec, errors):
    required = (
        player / "mpv.dll",
        player / "sounds" / "speaker_test.wav",
        player / "updater" / "main.py",
    )
    for path in required:
        if not path.is_file():
            errors.append(f"Required packaging asset is missing: {path.name}")
    for token in ("mpv.dll", "speaker_test.wav", "locale", "docs", "Updater.exe"):
        if token not in spec:
            errors.append(
                f"PyInstaller spec does not include packaging rule for {token}."
            )


def _check_updater(constants, installer, errors):
    marker = str(constants.get("APP_UPDATE_INSTALLER_MARKER") or "")
    if not marker or installer.count(marker) < 2:
        errors.append(
            "Installer updater marker disagrees with APP_UPDATE_INSTALLER_MARKER."
        )
    if "dist\\Updater.exe" not in installer:
        errors.append("Inno Setup does not package the component updater.")


def _check_release_names(repository, constants, errors):
    template = str(constants.get("APP_UPDATE_ASSET_TEMPLATE") or "")
    if template != "SimpleAudioPlayer-v{version}.{ext}":
        errors.append("Application release asset template is not canonical.")
    workflow = repository / ".github" / "workflows" / "release.yml"
    if workflow.is_file():
        text = workflow.read_text(encoding="utf-8")
        for suffix in ("exe", "zip"):
            if f"SimpleAudioPlayer-v$VERSION.{suffix}" not in text:
                errors.append(
                    f"Release workflow does not create canonical {suffix} asset."
                )


def _check_runtime_policy(player, spec, errors):
    policy = player / "youtube" / "RUNTIME_COMPONENTS.md"
    if not policy.is_file():
        errors.append("YouTube runtime component policy is not documented.")
    for executable in ("yt-dlp.exe", "deno.exe"):
        if executable in spec:
            errors.append(
                f"{executable} must be runtime-installed, not release-bundled."
            )


def main():
    errors = validate_project()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Project consistency checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
