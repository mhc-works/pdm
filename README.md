# PDM (Private Device Manager)

An app for managing and securing your own family's Android devices, with a server you host yourself.
PDM runs on the device as Device Owner, locks settings and app installs, reports app usage, and takes
its rules from your server.

**Status: nothing to install yet.** The repository starts with the checks that keep private data and
secrets out of it. The app and the server follow.

## What never goes into this repository

This repository is public. Files, commit messages, issues and pull requests hold no real host name,
IP or MAC address, email address, phone number, serial number, account, key, or private person's
name. Use `example.com`, `192.0.2.10` and "the admin".

`tools/check_public.py` enforces what a machine can check. Enable the hooks once per clone:

```
git config core.hooksPath .githooks
```

- Before a commit, the staged files and the commit message are checked.
- Before a push, the whole tree, the commits being pushed and the tests are checked.
- CI runs the same checks and [gitleaks](https://github.com/gitleaks/gitleaks) on every pull request.

A value the check refuses is either removed or, if it is public by nature, added to
`.public-allowlist`. Your own private words (real host names, names of people and places) go into
`.private-terms`, one per line. That file is git-ignored, and the check refuses any tracked file
that contains one of them.

Run everything by hand:

```
python3 tools/check_public.py
python3 tools/check_public.py FILE...
python3 -m unittest discover -s tests -v
```

The first checks every tracked file, the second the named files as they are on disk.

Sessions of Claude Code in this repository load `.claude/settings.json`. One hook runs
`tools/check_public.py` on each file Claude writes. Another refuses shell commands that skip or
redirect the git hooks or name the two private files (`.private-terms`, `devicetest/local.properties`).
The shell guard matches text, so it is a safety net, not a boundary. Machine-specific settings belong
in the git-ignored `.claude/settings.local.json`.

## Words and decisions

The project's terms are defined in [GLOSSARY.md](GLOSSARY.md), its decisions are recorded in
[docs/adr/](docs/adr/). English is the source language, and every text a person reads can be
translated; German is the first translation.

## Licence

PDM is free software under the [GNU Affero General Public License](LICENSE), version 3 or any later
version. [NOTICE](NOTICE) holds the attribution that must stay. To contribute, read
[CONTRIBUTING.md](CONTRIBUTING.md); to report a vulnerability, [SECURITY.md](SECURITY.md).
