# Architecture Notes

This is a living document for service boundaries and assumptions.

## Current boundary (through step 1.1.1.8)

- API entrypoint: `app/main.py`
- Framework: FastAPI
- Release/process tooling: `scripts/release.sh` + changelog fragments
- Persistence and ingestion layers: not implemented yet

## Determinism assumptions

- Tests must not call live HTTP services.
- Test data must be local and reproducible.
- Release behavior must be predictable (preflight checks, explicit confirmation).

## Near-term design direction (v1 scope)

- One-season ingest as the first bounded vertical slice.
- Keep domain logic isolated from web framework glue.
- Keep configuration explicit and environment-driven.
