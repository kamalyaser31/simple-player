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


def update_catalogs(pot_path):
    """Merge the template into every .po file and compile its .mo."""
    failures = 0
    for po_path in sorted((ROOT / "locale").glob("*/LC_MESSAGES/*.po")):
        language = po_path.parents[1].name
        try:
            subprocess.run(
                ["msgmerge", "-q", "-U", "--backup=none", str(po_path), str(pot_path)],
                check=True,
            )
            subprocess.run(
                ["msgfmt", "-c", "-o", str(po_path.with_suffix(".mo")), str(po_path)],
                check=True,
            )
        except FileNotFoundError:
            print("msgmerge or msgfmt was not found in PATH.", file=sys.stderr)
            return 2
        except subprocess.CalledProcessError as exc:
            print(f"{language}: failed with code {exc.returncode}.", file=sys.stderr)
            failures += 1
            continue
        print(f"Catalog updated: {language}")
    return 1 if failures else 0


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate the POT template with xgettext, then merge it into every "
            ".po catalog and compile the .mo files."
        )
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(ROOT / "locale" / "simple_audio_player.pot"),
        help="Output POT path.",
    )
    parser.add_argument(
        "--pot-only",
        action="store_true",
        help="Only generate the POT template; leave .po and .mo files untouched.",
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
        "--sort-by-file",
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
    if args.pot_only:
        return 0
    return update_catalogs(out_path)


if __name__ == "__main__":
    raise SystemExit(main())
