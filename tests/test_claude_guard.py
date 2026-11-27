"""The Claude Code hooks in .claude/hooks/guard.py refuse skipping the git hooks and private files.

Run from the repository root: python3 -m unittest discover -s tests -v
"""
import importlib.util
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("guard", ROOT / ".claude/hooks/guard.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

LONG_FLAG = "--no-" + "verify"
MAIL = "someone@" + "mailbox" + ".org"


class BashTest(unittest.TestCase):
    def test_refuses_skipping_or_redirecting_the_hooks_and_private_files(self):
        for command in (f"git commit {LONG_FLAG} -m x",
                        f"git commit {LONG_FLAG[:-1]} -m x",  # git accepts the flag abbreviated
                        f"git commit {LONG_FLAG[:-2]} -m x",
                        "git commit -n -m x",
                        "git commit -an -m x",
                        "git commit -nm x",
                        "git commit -n>out",
                        "git commit -m x \\\n  -n",
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
                        "git commit --no-verbose -m x",
                        "git commit -m x -- -n.txt",
                        "git commit -qm x\ngit log -n 3",
                        "git commit -F - <<'EOF'\nWhy commit -n is refused\nEOF",
                        "git config core.hooksPath .githooks",
                        "git config --get core.hooksPath",
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

    def test_reports_a_private_value_in_a_file_of_the_repository_unless_git_ignores_it(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = Path(tmp.name).resolve() / "repo"
        shutil.copytree(ROOT / "tools", repo / "tools")
        for name in (".public-allowlist", ".gitignore"):
            shutil.copy2(ROOT / name, repo / name)
        # Git hands a hook GIT_DIR and friends; this test must not inherit them from an outer hook.
        clean = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        with mock.patch.dict(os.environ, clean, clear=True), mock.patch.object(guard, "ROOT", repo):
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            for name, reported in (("note.md", True), ("work/note.md", False)):
                with self.subTest(name=name):
                    path = repo / name
                    path.parent.mkdir(exist_ok=True)
                    path.write_text(f"Write to {MAIL}.\n")
                    findings = guard.edit({"file_path": str(path)})
                    if reported:
                        self.assertIn("note.md:1: email address", findings)
                    else:
                        self.assertIsNone(findings)


if __name__ == "__main__":
    unittest.main()
