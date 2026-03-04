# Contributing

This is a solo-maintained project, but changes should still follow consistent rules.

## Workflow

1. Create focused commits.
2. Add or update tests when behavior changes.
3. Add a changelog fragment for any user-visible change.
4. Record significant architectural/process decisions in `spec/decisions.md`.

## Changelog fragments

- Place fragments in `changelog.d/`.
- Use `<issue-or-date>.<type>.md`.
- Valid types: `added`, `changed`, `fixed`, `removed`.

## Release ownership

- Releases are run manually with `scripts/release.sh`.
- Releases must end with an updated `CHANGELOG.md` and a matching `vX.Y.Z` tag.
