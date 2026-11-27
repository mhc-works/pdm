#!/usr/bin/env python3
"""Claude Code hooks for this public repository. Exit code 2 blocks and shows stderr to Claude.

    guard.py bash   PreToolUse on Bash: refuses skipping the git hooks and touching private files
    guard.py edit   PostToolUse on Edit|Write: runs tools/check_public.py on the written file
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIVATE_FILES = re.compile(r"(?<![\w.-])(?:\S*/)?(\.private-terms|local\.properties)(?![\w.-])")
SKIP_HOOKS = re.compile(r"--no-verify|\bgit\b[^|;&]*\bcommit\b[^|;&]*\s-[a-zA-Z]*n[a-zA-Z]*\b")


def bash(tool_input):
    command = tool_input.get("command", "")
    if SKIP_HOOKS.search(command):
        return "The git hooks of this repository are never skipped (CLAUDE.md). Fix what they report instead."
    match = PRIVATE_FILES.search(command)
    if match:
        return f"{match.group(1)} holds private values that must not enter the conversation; leave it to the admin."
    return None


def edit(tool_input):
    path = Path(tool_input.get("file_path", "")).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        return None
    if subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=ROOT).returncode == 0:
        return None  # never published
    result = subprocess.run([sys.executable, str(ROOT / "tools/check_public.py"), str(path)],
                            cwd=ROOT, capture_output=True, text=True)
    if result.returncode == 0:
        return None
    return (result.stdout + result.stderr).strip()


def main():
    reason = {"bash": bash, "edit": edit}[sys.argv[1]](json.load(sys.stdin).get("tool_input", {}))
    if reason:
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
