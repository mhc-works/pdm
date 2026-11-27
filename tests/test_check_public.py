"""tools/check_public.py refuses private data, in the patterns and through the real hooks.

The bad samples are put together from pieces, so that this file itself stays clean.

Run from the repository root: python3 -m unittest discover -s tests -v
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_public  # noqa: E402

ALLOW = check_public.Allowlist((ROOT / ".public-allowlist").read_text(encoding="utf-8"))

HOME_HOST = "nas.my" + "home" + ".net"
ROUTER_HOST = "fritz" + ".box"
LAN_IP = "192.168." + "10.10"
PUBLIC_IP = "84.12." + "34.56"
MAIL = "someone@" + "mailbox" + ".org"
MAC = "a4:5e:" + "60:c1:9b:02"
PHONE = "+49 " + "151 2345" + "6789"
PHONE_00 = "0049" + "15123456789"
TERM = "Musterhausen"


def kinds(text, terms=()):
    return [kind for _, kind, _ in check_public.scan_text(text, ALLOW, terms)]


class PatternTest(unittest.TestCase):
    def test_refuses_what_is_private(self):
        for sample, kind in ((f"server: {HOME_HOST}", "host name"),
                             (f"open http://{ROUTER_HOST}/ first", "host name"),
                             (f"https://{HOME_HOST}:8443/api", "host name"),
                             (f"adb connect {LAN_IP}:5555", "IP address"),
                             (f"reachable at {PUBLIC_IP}.", "IP address"),
                             (f"mail {MAIL} for access", "email address"),
                             (f"wlan0 {MAC}", "MAC address"),
                             (f"SMS to {PHONE}", "phone number"),
                             (f"call {PHONE_00}", "phone number")):
            with self.subTest(sample=sample):
                self.assertEqual([kind], kinds(sample))

    def test_accepts_placeholders_and_public_names(self):
        for sample in ("see https://github.com/mhc-works/pdm/issues/1",
                       "server: pdm.example.com, admin@example.com",
                       "adb connect 192.0.2.10:5555 or 127.0.0.1",
                       "https://www.gnu.org/licenses/ and docs.github.com",
                       "Co-Authored-By: Someone <12345+someone@users.noreply.github.com>",
                       "mac 00:00:00:00:00:00"):
            with self.subTest(sample=sample):
                self.assertEqual([], kinds(sample))

    def test_code_is_not_mistaken_for_addresses(self):
        for sample in ("import android.app.admin.DevicePolicyManager",
                       "import java.net.URL",
                       "val id = \"com.mhc_works.pdm\"",
                       "gitleaks 8.30.1, Android 16, One UI 8.5, plugin 1.5.74",
                       "sha256 0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0",
                       "tools/check_public.py --range A..B",
                       "at 12:30:45 on 2026-11-26",
                       "build.gradle.kts, settings.local.json, R.string.app_name"):
            with self.subTest(sample=sample):
                self.assertEqual([], kinds(sample))

    def test_private_term_is_found_in_any_case_and_never_echoed(self):
        found = list(check_public.scan_text(f"Tablet in {TERM.upper()}", ALLOW, [TERM]))
        self.assertEqual(["private term"], [kind for _, kind, _ in found])
        self.assertNotIn(TERM.lower(), found[0][2].lower())

    def test_allowlist_rejects_a_malformed_line(self):
        with self.assertRaises(ValueError):
            check_public.Allowlist("hostname example.com\n")

    def test_host_entry_does_not_cover_a_lookalike(self):
        self.assertEqual(["host name"], kinds("evil" + "github.com"))
        self.assertEqual(["host name"], kinds("github.com." + "attacker" + ".net"))


class HookTest(unittest.TestCase):
    """Real commits in a throwaway repository with the hooks switched on."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name) / "repo"
        self.repo.mkdir()
        for name in ("tools", ".githooks", ".public-allowlist", ".gitignore"):
            source = ROOT / name
            (shutil.copytree if source.is_dir() else shutil.copy2)(source, self.repo / name)
        # Git hands a hook GIT_DIR and friends; this test must not inherit them from an outer hook.
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.pop(check_public.TERMS_ENV, None)
        self.env["PATH"] = self.no_gitleaks_path()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "core.hooksPath", ".githooks")
        self.git("add", "-A")
        self.git("commit", "-qm", "start")

    def no_gitleaks_path(self):
        # gitleaks has its own job in CI; here only our check decides.
        return os.pathsep.join(p for p in os.environ.get("PATH", "").split(os.pathsep)
                               if not (Path(p) / "gitleaks").exists())

    def git(self, *args, check=True, env=None):
        result = subprocess.run(["git", *args], cwd=self.repo, env=env or self.env, capture_output=True, text=True)
        if check and result.returncode != 0:
            self.fail(f"git {' '.join(args)}: {result.stdout}{result.stderr}")
        return result

    def commit(self, name, content, message="change", env=None):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode())
        self.git("add", "--", name)
        return self.git("commit", "-qm", message, check=False, env=env)

    def check_named(self, name):
        return subprocess.run([sys.executable, "tools/check_public.py", name], cwd=self.repo,
                              env=self.env, capture_output=True, text=True)

    def head_has(self, name):
        return self.git("cat-file", "-e", f"HEAD:{name}", check=False).returncode == 0

    def test_clean_file_is_committed(self):
        result = self.commit("docs/setup.md", "Connect to pdm.example.com at 192.0.2.10.\n")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(self.head_has("docs/setup.md"))

    def test_named_files_are_checked_even_when_untracked(self):
        (self.repo / "new.md").write_text(f"Write to {MAIL}.\n")
        (self.repo / "clean.md").write_text("Write to the admin.\n")
        self.assertEqual(1, self.check_named("new.md").returncode)
        self.assertEqual(0, self.check_named(str(self.repo / "clean.md")).returncode)

    def test_named_tracked_file_is_read_as_on_disk_not_from_the_index(self):
        self.assertEqual(0, self.commit("note.md", "Write to the admin.\n").returncode)
        (self.repo / "note.md").write_text(f"Write to {MAIL}.\n")
        self.assertEqual(1, self.check_named("note.md").returncode)

    def test_private_values_in_a_file_are_refused(self):
        for index, bad in enumerate((HOME_HOST, LAN_IP, MAIL, MAC, PHONE)):
            with self.subTest(bad=bad):
                name = f"docs/note{index}.md"
                result = self.commit(name, f"value: {bad}\n")
                self.assertNotEqual(0, result.returncode)
                self.assertIn(name, result.stdout + result.stderr)
                self.assertFalse(self.head_has(name))
                self.git("reset", "-q", "--hard")

    def test_the_staged_content_counts_not_the_working_file(self):
        path = self.repo / "note.md"
        path.write_text(f"ip {LAN_IP}\n")
        self.git("add", "note.md")
        path.write_text("ip removed\n")
        self.assertNotEqual(0, self.git("commit", "-qm", "note", check=False).returncode)

    def test_private_value_in_the_commit_message_is_refused(self):
        result = self.commit("ok.md", "fine\n", message=f"Fix sync with {HOME_HOST}")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("commit message", result.stdout + result.stderr)
        self.assertFalse(self.head_has("ok.md"))

    def test_private_value_in_a_file_name_is_refused(self):
        result = self.commit(f"backup-{LAN_IP}.md", "fine\n")
        self.assertNotEqual(0, result.returncode)

    def test_file_that_is_not_text_is_refused(self):
        result = self.commit("dump.bin", b"\xff\xfe\x00\x01 not text")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("unreadable file", result.stdout + result.stderr)

    def test_private_terms_file_is_used_and_cannot_be_committed(self):
        (self.repo / ".private-terms").write_text(f"# my words\n{TERM}\n")
        result = self.commit("docs/place.md", f"The tablet lives in {TERM}.\n")
        self.assertNotEqual(0, result.returncode)
        self.assertNotIn(TERM, result.stdout + result.stderr)
        self.git("reset", "-q", "--hard")
        self.assertNotEqual(0, self.git("add", ".private-terms", check=False).returncode)

    def test_private_terms_from_the_environment(self):
        env = dict(self.env, **{check_public.TERMS_ENV: f"other\n{TERM}"})
        self.assertNotEqual(0, self.commit("docs/place.md", f"in {TERM}\n", env=env).returncode)

    def test_range_finds_a_private_author_address(self):
        self.git("-c", f"user.email={MAIL}", "commit", "-q", "--allow-empty", "-m", "empty")
        result = subprocess.run([sys.executable, "tools/check_public.py", "--range", "HEAD"], cwd=self.repo,
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertIn("email address", result.stdout)

    def test_pre_push_refuses_a_private_commit_made_without_hooks(self):
        remote = self.repo.parent / "remote.git"
        subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True, env=self.env)
        self.git("remote", "add", "origin", str(remote))
        (self.repo / "tests").mkdir()
        (self.repo / "leak.md").write_text(f"ip {LAN_IP}\n")
        self.git("add", "-A")
        self.git("-c", "core.hooksPath=/dev/null", "commit", "-qm", "sneaked in")
        result = self.git("push", "-q", "origin", "main", check=False)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("leak.md", result.stdout + result.stderr)
        listed = subprocess.run(["git", "ls-remote", str(remote)], capture_output=True, text=True, env=self.env)
        self.assertEqual("", listed.stdout)


class ThisRepositoryTest(unittest.TestCase):
    def test_every_tracked_file_is_clean(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        result = subprocess.run([sys.executable, "tools/check_public.py"], cwd=ROOT, env=env,
                                capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
