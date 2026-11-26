## This repository is public

Files, file names, commit messages, issues and pull requests hold no real host name, IP or MAC address, email address, phone number, serial number, account, key, or private person's name. Use `example.com`, `192.0.2.10` and "the admin". Enable the hooks once per clone with `git config core.hooksPath .githooks`; `tools/check_public.py` and the tests in `tests/` enforce what a machine can check (see `README.md`). Never skip a hook with `--no-verify`.

## Language

English is the source language; every text a person reads must be translatable (`docs/adr/0004-english-source-every-text-translatable.md`).

## Agent skills

### Issue tracker

Issues live in GitHub Issues of `mhc-works/pdm` (via the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

The five default triage labels (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), plus `security-review`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
