#!/usr/bin/env python3
"""Refuses anything private in what this public repository tracks.

Finds host names, IP and MAC addresses, email addresses and phone numbers that are not on the
allowlist (.public-allowlist), files that cannot be read as text, and the private terms of the
person running it. The terms (real host names, people's names, places) are never tracked: they come
from the git-ignored file .private-terms, one per line, or from the PDM_PRIVATE_TERMS variable.

    tools/check_public.py                 every tracked file
    tools/check_public.py --staged        what the next commit holds (pre-commit hook)
    tools/check_public.py --message FILE  a commit message (commit-msg hook)
    tools/check_public.py --range A..B    the messages of those commits (pre-push hook, CI)
    tools/check_public.py FILE...         those files as they are on disk (Claude Code edit hook)

Exit code 0: clean. 1: findings, one per line. 2: it could not run.
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ".public-allowlist"
TERMS_FILE = ".private-terms"
TERMS_ENV = "PDM_PRIVATE_TERMS"

# Files that are not text. Anything else that does not decode as UTF-8 is a finding.
BINARY_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".ttf", ".otf", ".woff", ".woff2", ".jar")

# Endings that make a dotted word a host name. Anything ending in one of these must be on the allowlist.
TLDS = ("com|net|org|de|dev|io|app|eu|info|me|ch|at|uk|us|fr|nl|it|es|pl|se|no|dk|fi|cz|be|lu|tv|cc|co|xyz|online|"
        "site|cloud|page|link|home|lan|local|internal|intranet|box|arpa|onion|duckdns|ts")
HOST = re.compile(r"(?<![\w.@-])((?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:%s))(?![\w-])(?!\.[a-z0-9])" % TLDS, re.I)
EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@((?:[a-z0-9-]+\.)+[a-z]{2,})(?![\w-])", re.I)
IPV4 = re.compile(r"(?<![\w.])(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(?![\w]|\.\d)")
MAC = re.compile(r"(?<![\w:])(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}(?![\w:])", re.I)
PHONE = re.compile(r"(?<![\w.+])(?:\+|00)[1-9]\d(?:[ /()-]{0,2}\d){6,}(?!\w)")


class Allowlist:
    """Lines of `host NAME`, `ip ADDRESS-OR-PREFIX`, `email ADDRESS`, `mac ADDRESS`, `phone NUMBER`."""

    def __init__(self, text):
        self.entries = {"host": set(), "ip": set(), "email": set(), "mac": set(), "phone": set()}
        for number, line in enumerate(text.splitlines(), 1):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            kind, _, value = line.partition(" ")
            if kind not in self.entries or not value.strip():
                raise ValueError(f"{ALLOWLIST}:{number}: expected '<host|ip|email|mac|phone> <value>'")
            self.entries[kind].add(value.strip().lower())

    def host(self, name):
        name = name.lower()
        return any(name == allowed or name.endswith("." + allowed) for allowed in self.entries["host"])

    def ip(self, address):
        return any(address == allowed or (allowed.endswith(".") and address.startswith(allowed))
                   for allowed in self.entries["ip"])

    def exact(self, kind, value):
        return value.lower() in self.entries[kind]


def digits(text):
    return re.sub(r"\D", "", text)


def scan_text(text, allow, terms=()):
    """Yields (line number, kind, what was found) for one text. A private term is never echoed."""
    lowered_terms = [t.lower() for t in terms if t.strip()]
    for number, line in enumerate(text.splitlines(), 1):
        emails = set()
        for match in EMAIL.finditer(line):
            emails.add(match.span(1))
            if not allow.exact("email", match.group(0)) and not allow.host(match.group(1)):
                yield number, "email address", match.group(0)
        for match in HOST.finditer(line):
            if match.span(1) not in emails and not allow.host(match.group(1)):
                yield number, "host name", match.group(1)
        for match in IPV4.finditer(line):
            if all(int(part) <= 255 for part in match.groups()) and not allow.ip(match.group(0)):
                yield number, "IP address", match.group(0)
        for match in MAC.finditer(line):
            if not allow.exact("mac", match.group(0)):
                yield number, "MAC address", match.group(0)
        for match in PHONE.finditer(line):
            if digits(match.group(0)) not in {digits(p) for p in allow.entries["phone"]}:
                yield number, "phone number", match.group(0)
        low = line.lower()
        for index, term in enumerate(lowered_terms, 1):
            if term in low:
                yield number, "private term", f"#{index} of the private list"


def git(*args, binary=False):
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout if binary else result.stdout.decode()


def load_terms():
    terms = []
    path = ROOT / TERMS_FILE
    if path.exists():
        terms += path.read_text(encoding="utf-8").splitlines()
    terms += os.environ.get(TERMS_ENV, "").splitlines()
    return [t.strip() for t in terms if t.strip() and not t.lstrip().startswith("#")]


def scan_files(names, read, allow, terms):
    findings = []
    for name in names:
        # The name of a file is published too.
        findings += [(name, 0, kind, what) for _, kind, what in scan_text(name, allow, terms)]
        if name.lower().endswith(BINARY_SUFFIXES):
            continue
        try:
            text = read(name).decode("utf-8")
        except UnicodeDecodeError:
            findings.append((name, 0, "unreadable file", "not UTF-8 text and not a known binary type"))
            continue
        findings += [(name, number, kind, what) for number, kind, what in scan_text(text, allow, terms)]
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true")
    mode.add_argument("--message", metavar="FILE")
    mode.add_argument("--range", metavar="A..B")
    mode.add_argument("files", nargs="*", metavar="FILE", default=[])
    args = parser.parse_args(argv)
    try:
        allow = Allowlist((ROOT / ALLOWLIST).read_text(encoding="utf-8"))
        terms = load_terms()
        if args.message:
            text = Path(args.message).read_text(encoding="utf-8", errors="replace")
            # Lines git itself drops from the message.
            text = "\n".join(line for line in text.splitlines() if not line.startswith("#"))
            findings = [("commit message", n, k, w) for n, k, w in scan_text(text, allow, terms)]
        elif args.range:
            findings = []
            for commit in git("rev-list", args.range).split():
                message = git("show", "-s", "--format=%an <%ae>%n%cn <%ce>%n%B", commit)
                findings += [(f"commit {commit[:9]}", n, k, w) for n, k, w in scan_text(message, allow, terms)]
        elif args.staged:
            names = [n for n in git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split("\0") if n]
            findings = scan_files(names, lambda n: git("show", f":{n}", binary=True), allow, terms)
        elif args.files:
            names = [os.path.relpath(Path(f).resolve(), ROOT) for f in args.files]
            findings = scan_files(names, lambda n: (ROOT / n).read_bytes(), allow, terms)
        else:
            names = [n for n in git("ls-files", "-z").split("\0") if n]
            findings = scan_files(names, lambda n: (ROOT / n).read_bytes(), allow, terms)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"check_public: {error}", file=sys.stderr)
        return 2
    for where, number, kind, what in findings:
        print(f"{where}:{number}: {kind}: {what}" if number else f"{where}: {kind}: {what}")
    if findings:
        print(f"check_public: {len(findings)} finding(s). Remove them, or add a public value to {ALLOWLIST}.",
              file=sys.stderr)
        return 1
    if not terms:
        print(f"check_public: no private terms loaded ({TERMS_FILE} or ${TERMS_ENV}); patterns only.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
