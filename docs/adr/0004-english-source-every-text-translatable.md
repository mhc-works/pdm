# English is the source language, and every text a person reads is translatable

PDM is public, and its first users read German. Decided on 2026-11-26: English is the source language of code, documentation and every text shown to a person; all such texts can be translated, and German is the first translation.

## Considered Options

- **German only:** fits the first users, shuts out everyone else and would have to be undone later across the whole code.
- **English only:** simplest, but the first users would not understand their own devices.

## Consequences

- **App:** no text shown to a person is written in code or layouts. Every one is a string resource, English in `values/`, translations in `values-<language>/`. Android lint treats a hard-coded text as an error, so the build fails on one.
- **Server and its pages:** every text shown to a person comes from a message catalogue by key, never from the code. The language follows the person's setting, with English as the fallback.
- **Between app and server:** messages carry codes and values, never finished sentences. Each side turns a code into text in its own language.
- **Formats:** dates, times, numbers and durations are formatted for the person's locale by the platform, never by hand.
- **Documentation:** written in English at the repository root and in `docs/`. A translation of a document goes to `docs/<language>/` under the same file name; the English version decides when they differ.
- **Glossary:** the English term is the one used in code and documents. Each entry names its German counterpart, which is the word the German translation uses.
- **Not translated:** log lines, developer tools such as `tools/check_public.py`, commit messages and code comments stay English.
