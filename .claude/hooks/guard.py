#!/usr/bin/env python3
"""Claude Code hooks for this public repository. Exit code 2 blocks and shows stderr to Claude.

    guard.py bash   PreToolUse on Bash: refuses skipping or redirecting the git hooks and touching private files
    guard.py edit   PostToolUse on Edit|Write|MultiEdit|NotebookEdit: runs tools/check_public.py on the written file
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIVATE_FILES = re.compile(r"(?<![\w.-])(?:\S*/)?(\.private-terms|local\.properties)(?![\w.-])")
# Skipping the hooks: the long flag or an abbreviation git accepts for it (from --no-veri on), the
# short flag -n (alone or bundled) on a commit, or redirecting the hooks directory, except for the
# documented setup `git config core.hooksPath .githooks` and for reading the setting with --get.
# A commit ends at the end of its line, unless a backslash continues the line.
SAME_COMMAND = r"(?:[^|;&\n\\]|\\\n|\\)*"
SKIP_HOOKS = re.compile(
    r"--no-veri"
    r"|\bgit\b" + SAME_COMMAND + r"\bcommit\b" + SAME_COMMAND + r"\s-[a-zA-Z]*n[a-zA-Z]*\b(?!\.)"
    r"|(?<!--get )(?i:core\.hooksPath)(?!\s+\.githooks(?![\w./-]))")


def bash(tool_input):
    command = tool_input.get("command", "")
    if SKIP_HOOKS.search(command):
        return "The git hooks of this repository are never skipped (CLAUDE.md). Fix what they report instead."
    match = PRIVATE_FILES.search(command)
    if match:
        return f"{match.group(1)} holds private values that must not enter the conversation; leave it to the admin."
    return None


def edit(tool_input):
    name = tool_input.get("file_path") or tool_input.get("notebook_path")  # NotebookEdit uses the latter
    if not name:
        return None
    path = Path(name).resolve()
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
