# Contributing

Contributions are welcome as pull requests to [mhc-works/pdm](https://github.com/mhc-works/pdm).
Every change reaches `main` through a pull request, never by a direct push.

## Before you start

- Enable the hooks: `git config core.hooksPath .githooks`. They refuse private data and secrets, as
  the [README](README.md) describes. Nothing private goes into a file, a commit message, an issue or
  a pull request.
- Run `python3 tools/check_public.py` and `python3 -m unittest discover -s tests -v` and fix what
  they report.

## Sign-off (DCO)

You confirm each contribution with the [Developer Certificate of Origin](https://developercertificate.org/):
you wrote the change or have the right to submit it under this project's licence, AGPL-3.0-or-later.
Say so on every commit by adding a sign-off line, which `git commit -s` writes for you:

```
Signed-off-by: Your Name <you@example.com>
```

A pull request with a commit that lacks it is asked to add it before it is merged.

## Licence

Your contribution is licensed under the [AGPL-3.0-or-later](LICENSE) like the rest of the project.
The attribution in [NOTICE](NOTICE) stays.

## Security

Report vulnerabilities privately, as [SECURITY.md](SECURITY.md) says.
