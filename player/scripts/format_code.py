import argparse
import subprocess
import sys
from pathlib import Path


def run_formatter(target_path):
    target = Path(target_path).resolve()
    if not target.exists():
        print(f"Target path '{target}' does not exist.")
        return 1

    print(f"Running black formatter on: {target}")

    # 1. Run black to format
    black_cmd = [sys.executable, "-m", "black", "--exclude", "mpv\\.py", str(target)]
    try:
        subprocess.run(black_cmd, check=True)
        print("Formatting complete via black.")
    except FileNotFoundError:
        print(
            "black is not installed or not found. Please install it using 'pip install black'."
        )
        return 2
    except subprocess.CalledProcessError as exc:
        print(f"black formatting failed with exit code {exc.returncode}")
        return exc.returncode

    # 2. Run flake8 to check style
    print(f"\nRunning flake8 linter on: {target}")
    exclude_flag = "--exclude=.venv,venv,build,dist,__pycache__,*.egg-info,mpv.py"
    flake8_cmd = [
        sys.executable,
        "-m",
        "flake8",
        exclude_flag,
        "--max-line-length=88",
        "--ignore=E203,W503,E501,W391",
        "--builtins=_",
        str(target),
    ]
    try:
        result = subprocess.run(flake8_cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("flake8 check passed! No style issues found.")
        else:
            print("flake8 found style issues:")
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return result.returncode
    except FileNotFoundError:
        print(
            "flake8 is not installed or not found. Please install it using 'pip install flake8'."
        )
        return 3

    return 0


def main():
    script_dir = Path(__file__).resolve().parent
    # Default target is the player directory (parent of scripts)
    default_target = script_dir.parent

    parser = argparse.ArgumentParser(
        description="Format python files using black and lint with flake8."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=str(default_target),
        help="Target folder or file to format/lint (default: player directory).",
    )
    args = parser.parse_args()

    return run_formatter(args.target)


if __name__ == "__main__":
    raise SystemExit(main())
