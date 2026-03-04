# F1 Prediction Model

Deterministic API project for Formula 1 data ingestion, baseline race prediction, and simulation.

## Current State

- Version: `0.1.0`
- Phase: Version 0 (environment + release tooling baseline)

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
./.venv/bin/python -m pytest -q
uvicorn app.main:app --reload
```

## State Map

See [Project Manual - State S0](./Project_Manual.md) for the Version 0 gate and progression into Version 1.

## Project History

- [CHANGELOG](./CHANGELOG.md)
- [Decisions Log](./spec/decisions.md)

## Release Policy

- Releases are tagged as `vX.Y.Z`.
- Every release updates `pyproject.toml` version and `CHANGELOG.md`.
- Changelog entries are collected as fragments under `changelog.d/` and compiled during release.
