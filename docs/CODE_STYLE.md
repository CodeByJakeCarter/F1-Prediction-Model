# Code Style

## Python conventions

- Follow PEP 8 defaults.
- Use type hints for public functions.
- Prefer small pure functions for domain logic.
- Keep FastAPI route handlers thin.

## Testing conventions

- Use `pytest`.
- Name tests by behavior (for example, `test_release_fails_on_dirty_tree`).
- Do not make live network calls in tests.

## Repository conventions

- One focused change per commit when practical.
- Add a changelog fragment for user-visible behavior changes.
- Record architectural decisions in `spec/decisions.md`.
