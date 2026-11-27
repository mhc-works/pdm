## This repository is public

Files, file names, commit messages, issues and pull requests hold no real host name, IP or MAC address, email address, phone number, serial number, account, key, or private person's name. Use `example.com`, `192.0.2.10` and "the admin". Enable the hooks once per clone with `git config core.hooksPath .githooks`; `tools/check_public.py` and the tests in `tests/` enforce what a machine can check (see `README.md`). Never skip a hook with `--no-verify`.

## Language

English is the source language; every text a person reads must be translatable (`docs/adr/0004-english-source-every-text-translatable.md`).

## Code maintenance

Every coding task follows the `ponytail` skill at level `full`: the smallest change that fully solves the task. Subagents that touch code get the same rule in their brief.

## Agent skills

### Issue tracker

Issues live in GitHub Issues of `mhc-works/pdm` (via the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

The five default triage labels (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), plus `security-review`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
