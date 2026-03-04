# F1 Prediction Model

Minimal FastAPI starter for building an F1 prediction service.

## Project structure

```text
.
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_health.py
├── .env.example
├── pyproject.toml
├── README.md
└── RUNBOOK.md
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

## Run tests

```bash
pytest
```
