# Local environment bootstrap

1. Create a virtual environment:
   `python -m venv .venv`
2. Activate it:
   `source .venv/bin/activate`
3. Upgrade pip:
   `python -m pip install --upgrade pip`
4. Install project + dev dependencies:
   `pip install -e ".[dev]"`
5. Run tests:
   `pytest -q`

# Run the API locally

1. Activate virtual environment:
   `source .venv/bin/activate`
2. Start API server:
   `uvicorn app.main:app --reload`
3. Check health:
   `curl http://127.0.0.1:8000/health`

# Ingest workflow (current state)

- Ingestion pipeline is not implemented yet at step `1.1.1.8`.
- Planned v1 target is one-season deterministic ingest (implemented in later manual steps).
- Until ingest exists, do not add ad-hoc scripts that bypass deterministic test rules.

# Deterministic test environment rules

- No live HTTP calls in tests.
- Never point tests at production or shared databases.
- Use only local/ephemeral test data and deterministic inputs.

# Manual release process

1. Ensure the working tree is clean:
   `git status --short`
2. Add changelog fragments under `changelog.d/`.
3. Run release dry-run:
   `./scripts/release.sh --version X.Y.Z --dry-run`
4. Run release for real:
   `./scripts/release.sh --version X.Y.Z --yes`
5. Push commit and tag:
   `git push && git push --tags`

# Rollback guidance

- If release script fails before commit/tag: fix issue and re-run.
- If commit exists but tag should be corrected:
  - delete local tag: `git tag -d vX.Y.Z`
  - delete remote tag (if pushed): `git push --delete origin vX.Y.Z`
  - create corrected release with a new version.
- Never rewrite published history for released tags.
