"""PostToolUse hook: run the test suite after Claude edits a file.

Claude Code pipes a JSON description of the edit on stdin. If the edited file
is inside this repo, run `pytest -q -x`. On failure, print pytest's output to
stderr and exit 2 so Claude sees the failure right away and can fix it.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])


def pick_python() -> str:
    # Prefer the repo's virtualenv (Windows or macOS/Linux layout), so the hook
    # works even when Claude was started outside an activated venv.
    for candidate in (ROOT / ".venv" / "Scripts" / "python.exe", ROOT / ".venv" / "bin" / "python"):
        if candidate.exists():
            return str(candidate)
    return sys.executable


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = {}
    file_path = (payload.get("tool_input") or {}).get("file_path", "")

    # Skip edits outside this repo (e.g. notes in another folder).
    if file_path:
        try:
            Path(file_path).resolve().relative_to(ROOT.resolve())
        except ValueError:
            return 0

    try:
        result = subprocess.run(
            [pick_python(), "-m", "pytest", "-q", "-x", "--no-header", "-p", "no:cacheprovider"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=110,
        )
    except subprocess.TimeoutExpired:
        print("pytest timed out after 110s", file=sys.stderr)
        return 2

    if result.returncode in (0, 5):  # 5 = no tests collected
        return 0

    output = (result.stdout + result.stderr).strip()
    print(f"Tests failed after editing {file_path or 'a file'}:\n\n{output[-4000:]}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
