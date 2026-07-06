import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {"__pycache__", ".git", ".venv", "venv", "dist", "build"}


def iter_py_files(root):
    for path in root.rglob("*.py"):
        parts = set(path.parts)
        if parts.intersection(EXCLUDE_DIRS):
            continue
        yield path


def main():
    parser = argparse.ArgumentParser(description="Generate POT template using xgettext.")
    parser.add_argument(
        "-o",
        "--output",
        default=str(ROOT / "locale" / "simple_audio_player.pot"),
        help="Output POT path.",
    )
    args = parser.parse_args()

    files = sorted(iter_py_files(ROOT))
    if not files:
        print("No Python files found.")
        return 1

    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        delete=False,
        suffix=".lst",
    ) as lst:
        list_path = Path(lst.name)
        for path in files:
            rel = path.relative_to(ROOT).as_posix()
            lst.write(rel + "\n")

    cmd = [
        "xgettext",
        "--language=Python",
        "--from-code=UTF-8",
        "--keyword=_",
        "--sort-output",
        "--files-from",
        str(list_path),
        "--output",
        str(out_path),
    ]
    try:
        subprocess.run(cmd, cwd=str(ROOT), check=True)
    except FileNotFoundError:
        print("xgettext was not found in PATH.")
        return 2
    except subprocess.CalledProcessError as exc:
        print(f"xgettext failed with code {exc.returncode}.")
        return exc.returncode
    finally:
        try:
            os.unlink(list_path)
        except OSError:
            pass

    print(f"Template generated: {out_path}")
    print(f"Files scanned: {len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
