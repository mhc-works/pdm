"""The licence and the papers around it.

Run from the repository root: python3 -m unittest discover -s tests -v
"""
import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "mhc-works/pdm"
# gnu.org/licenses/agpl-3.0.txt
AGPL_SHA256 = "0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0"


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


class LicenceTest(unittest.TestCase):
    def test_license_is_the_agpl_3_text(self):
        self.assertEqual(AGPL_SHA256, hashlib.sha256((ROOT / "LICENSE").read_bytes()).hexdigest())

    def test_notice_states_agpl_or_later_and_the_7b_term(self):
        text = read("NOTICE")
        self.assertIn("AGPL-3.0-or-later", text)
        self.assertIn("section 7(b)", text)
        self.assertIn('"PDM, by mhc-works"', text)
        self.assertIn("About screen", text)

    def test_readme_names_the_licence_and_the_rules(self):
        text = read("README.md")
        self.assertIn("GNU Affero General Public License", text)
        self.assertIn("git config core.hooksPath .githooks", text)
        self.assertIn(".private-terms", text)

    def test_contributing_names_dco(self):
        text = read("CONTRIBUTING.md")
        self.assertIn("Signed-off-by", text)
        self.assertIn("AGPL-3.0-or-later", text)

    def test_security_names_private_reporting_of_this_repo(self):
        text = read("SECURITY.md")
        self.assertIn(REPOSITORY, text)
        self.assertRegex(text, re.compile("private vulnerability reporting", re.I))


if __name__ == "__main__":
    unittest.main()
