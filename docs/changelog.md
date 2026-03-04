# Changelog Rules

- Do not edit historical release entries in `CHANGELOG.md` except for corrections.
- Add new work as fragments in `changelog.d/`.
- Fragment filename format: `<issue-or-date>.<type>.md`.
- Valid types: `added`, `changed`, `fixed`, `removed`.
- Release process compiles fragments into `CHANGELOG.md` and clears processed fragments.
