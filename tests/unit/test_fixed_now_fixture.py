from datetime import UTC, datetime


def test_fixed_now_fixture_is_deterministic(fixed_now) -> None:
    assert fixed_now == datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    assert fixed_now.isoformat() == "2024-01-01T12:00:00+00:00"
