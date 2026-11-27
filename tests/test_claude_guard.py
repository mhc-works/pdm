"""The Claude Code hooks in .claude/hooks/guard.py refuse skipping the git hooks and private files.

Run from the repository root: python3 -m unittest discover -s tests -v
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("guard", ROOT / ".claude/hooks/guard.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

LONG_FLAG = "--no-" + "verify"


class BashTest(unittest.TestCase):
    def test_refuses_skipping_or_redirecting_the_hooks_and_private_files(self):
        for command in (f"git commit {LONG_FLAG} -m x",
                        "git commit -n -m x",
                        "git commit -an -m x",
                        "git commit -nm x",
                        "git commit -n>out",
                        'git commit -n"" -m x',
                        f"git push {LONG_FLAG}",
                        "git -c core.hooksPath=/dev/null commit -m x",
                        "git config core.hookspath /tmp/x",
                        "git config --unset core.hooksPath",
                        "cat .private-terms",
                        "cat devicetest/local.properties"):
            with self.subTest(command=command):
                self.assertIsInstance(guard.bash({"command": command}), str)

    def test_allows_ordinary_commands(self):
        for command in ("git commit -m x",
                        "git commit --no-edit",
                        "git commit -m x -- -n.txt",
                        "git config core.hooksPath .githooks",
                        "git status"):
            with self.subTest(command=command):
                self.assertIsNone(guard.bash({"command": command}))


class EditTest(unittest.TestCase):
    def test_ignores_a_file_outside_the_repository(self):
        with tempfile.NamedTemporaryFile(suffix=".md") as outside:
            for key in ("file_path", "notebook_path"):
                with self.subTest(key=key):
                    self.assertIsNone(guard.edit({key: outside.name}))

    def test_ignores_empty_input(self):
        self.assertIsNone(guard.edit({}))


if __name__ == "__main__":
    unittest.main()
