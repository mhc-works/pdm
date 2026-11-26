"""Nothing local, secret or built is tracked; .gitignore, the hooks and CI keep it that way.

Run from the repository root: python3 -m unittest discover -s tests -v
"""
import os
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
LOCAL_DIRS = ("work/", "backup/", "shots/", "secrets/", "graphify-out/", ".claude/worktrees/")
LOCAL_SUFFIXES = (".apk", ".aab", ".jks", ".keystore", ".pem", ".key", ".p12", ".pfx", ".token")
LOCAL_NAMES = ("local.properties", "keystore.properties", ".private-terms")
# What .gitignore must ignore, probed with `git check-ignore` on paths that do not exist.
MUST_IGNORE = (".private-terms", ".env", ".env.local", "app/local.properties", "keystore.properties", "secrets/x",
               "release.jks", "upload.keystore", "server.pem", "server.key", "id_ed25519", "id_ed25519.pub",
               "tools/adbkey", "tools/adbkey.pub", "app/build/x", "app/release/pdm.apk", "pdm.aab", "work/x",
               "backup/x", "shots/x.png", ".claude/settings.local.json")


def tracked():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, env=ENV, capture_output=True, text=True, check=True)
    return [name for name in out.stdout.split("\0") if name]


class PublicTreeTest(unittest.TestCase):
    def test_no_local_directory_is_tracked(self):
        self.assertEqual([], [n for n in tracked() if n.startswith(LOCAL_DIRS)])

    def test_no_key_secret_or_package_file_is_tracked(self):
        bad = [n for n in tracked() if n.endswith(LOCAL_SUFFIXES) or Path(n).name in LOCAL_NAMES
               or Path(n).name.startswith((".env", "adbkey", "id_ed25519"))]
        self.assertEqual([], bad)

    def test_gitignore_covers_them(self):
        missing = [p for p in MUST_IGNORE
                   if subprocess.run(["git", "check-ignore", "-q", p], cwd=ROOT, env=ENV).returncode != 0]
        self.assertEqual([], missing)

    def test_code_owners_file_has_the_name_github_reads(self):
        # GitHub reads CODEOWNERS only; a file with another spelling is silently ignored.
        owners = [n for n in tracked() if Path(n).name.upper().startswith("CODEOWNER")]
        self.assertEqual([".github/CODEOWNERS"], owners)
        rules = [line for line in (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8").splitlines()
                 if line.strip() and not line.startswith("#")]
        self.assertTrue(rules)
        for rule in rules:
            self.assertRegex(rule, r"^\S+(\s+@[\w-]+(/[\w-]+)?)+$")

    def test_hooks_are_executable_and_run_the_check(self):
        for name in ("pre-commit", "commit-msg", "pre-push"):
            hook = ROOT / ".githooks" / name
            self.assertTrue(os.access(hook, os.X_OK), name)
            self.assertIn("tools/check_public.py", hook.read_text(encoding="utf-8"), name)


class WorkflowTest(unittest.TestCase):
    """Code from a fork must never get secrets or write access."""

    def workflows(self):
        files = sorted((ROOT / ".github" / "workflows").glob("*.y*ml"))
        self.assertTrue(files)
        return [(f.name, f.read_text(encoding="utf-8")) for f in files]

    def code(self, text):
        return "\n".join(line.split(" #", 1)[0] for line in text.splitlines() if not line.lstrip().startswith("#"))

    def test_no_workflow_runs_on_pull_request_target(self):
        for name, text in self.workflows():
            self.assertNotIn("pull_request_target", self.code(text), name)

    def test_token_is_read_only_by_default(self):
        for name, text in self.workflows():
            self.assertRegex(self.code(text), r"(?m)^permissions:\n  contents: read\n", name)
            self.assertNotRegex(self.code(text), r":\s*write\b", name)

    def test_actions_are_pinned_to_a_commit(self):
        for name, text in self.workflows():
            for ref in re.findall(r"uses:\s*(\S+)", text):
                self.assertRegex(ref, r"@[0-9a-f]{40}$", f"{name}: {ref}")

    def test_dependabot_keeps_the_pinned_actions_current(self):
        text = (ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^version: 2$")
        self.assertRegex(text, r"(?m)^\s+- package-ecosystem: github-actions$")
        self.assertRegex(text, r"(?m)^\s+directory: /$")

    def test_ci_runs_the_check_the_tests_and_gitleaks(self):
        ci = dict(self.workflows())["ci.yml"]
        for needed in ("tools/check_public.py", "--range HEAD", "unittest discover", "gitleaks detect", "sha256sum -c"):
            self.assertIn(needed, ci)


if __name__ == "__main__":
    unittest.main()
