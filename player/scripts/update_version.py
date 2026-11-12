import json
import re
import subprocess
import sys
import os


def update_version(new_version):
    # This script is in /player/scripts/
    # script_dir = /player/scripts/
    # player_dir = /player/
    # repo_root = /
    script_dir = os.path.dirname(os.path.abspath(__file__))
    player_dir = os.path.dirname(script_dir)
    root_dir = os.path.dirname(player_dir)

    # 1. Update info.json (Root)
    info_path = os.path.join(root_dir, "info.json")
    if os.path.exists(info_path):
        with open(info_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["version"] = new_version
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Updated {info_path} to {new_version}")
    else:
        print(f"Could not find {info_path}")

    # 2. Update config/constants.py
    constants_path = os.path.join(player_dir, "config", "constants.py")
    if os.path.exists(constants_path):
        with open(constants_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(
            r'APP_VERSION\s*=\s*".*?"', f'APP_VERSION = "{new_version}"', content
        )
        with open(constants_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {constants_path} to {new_version}")
    else:
        print(f"Could not find {constants_path}")

    # 3. Update simple_audio_player.iss
    iss_path = os.path.join(player_dir, "simple_audio_player.iss")
    if os.path.exists(iss_path):
        with open(iss_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(
            r'#define\s+MyAppVersion\s*".*?"',
            f'#define MyAppVersion "{new_version}"',
            content,
        )
        with open(iss_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {iss_path} to {new_version}")
    else:
        print(f"Could not find {iss_path}")


VERSION_PATTERN = re.compile(r"\d+\.\d+\.\d+")


def normalize_version(raw):
    """Return 'X.Y.Z' from input such as 'v1.6.0', or None if malformed."""
    version = str(raw or "").strip()
    if version[:1] in ("v", "V"):
        version = version[1:]
    return version if VERSION_PATTERN.fullmatch(version) else None


def run_consistency_check():
    script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "validate_project_consistency.py"
    )
    sys.stdout.flush()
    return subprocess.run([sys.executable, script]).returncode


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_version.py <version>")
        sys.exit(1)

    version = normalize_version(sys.argv[1])
    if version is None:
        print(
            f"Invalid version: {sys.argv[1]!r}. Use MAJOR.MINOR.PATCH, e.g. 1.6.0.",
            file=sys.stderr,
        )
        sys.exit(1)
    update_version(version)
    sys.exit(run_consistency_check())
