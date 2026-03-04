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

# Deterministic test environment rules

- No live HTTP calls in tests.
- Never point tests at production or shared databases.
- Use only local/ephemeral test data and deterministic inputs.
