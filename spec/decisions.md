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

## D-0002: Freeze v1 scope to one-season deterministic MVP

- Date: 2026-03-04
- Status: Accepted

### Context

Broad multi-season ingest and advanced modelling would increase delivery risk for v1.

### Decision

For v1, only ingest one full season and provide deterministic baseline prediction behavior.

### Consequences

- Faster path to a verifiable MVP.
- Clear acceptance target for integration and backtesting layers.

## D-0003: Explicit v1 non-goals

- Date: 2026-03-04
- Status: Accepted

### Context

Without non-goals, scope creep is likely during early implementation.

### Decision

The following are non-goals for v1:

- Multi-season historical ingestion.
- Production-grade deployment automation.
- Real-time/live race prediction feeds.

### Consequences

- Work remains focused on deterministic correctness first.
- Future versions can expand capability with less rework.
