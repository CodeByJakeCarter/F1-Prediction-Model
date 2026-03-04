from __future__ import annotations

from typing import Any


def assert_snapshot_like(actual: Any, expected: Any, float_tol: float = 1e-6) -> None:
    _assert_values(actual, expected, float_tol=float_tol)


def _assert_values(actual: Any, expected: Any, float_tol: float) -> None:
    if isinstance(actual, dict) and isinstance(expected, dict):
        assert sorted(actual.keys()) == sorted(expected.keys())
        for key in sorted(expected.keys()):
            _assert_values(actual[key], expected[key], float_tol=float_tol)
        return

    if isinstance(actual, list) and isinstance(expected, list):
        assert len(actual) == len(expected)
        for actual_item, expected_item in zip(actual, expected):
            _assert_values(actual_item, expected_item, float_tol=float_tol)
        return

    if isinstance(actual, float) and isinstance(expected, float):
        assert abs(actual - expected) <= float_tol
        return

    assert actual == expected
