# Decisions Log

## D-0001: Track releases with changelog fragments and tags

- Date: 2026-03-04
- Status: Accepted

### Context

The project needs a readable, low-friction release history that remains clean over time.

### Decision

Use fragment files in `changelog.d/`, compile them during release, and create a matching git tag for each release.

### Consequences

- Release flow is explicit and repeatable.
- Repository history is easier to audit.
