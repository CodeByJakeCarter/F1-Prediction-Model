from app.main import healthcheck


def test_healthcheck_returns_ok() -> None:
    assert healthcheck() == {"status": "ok"}
