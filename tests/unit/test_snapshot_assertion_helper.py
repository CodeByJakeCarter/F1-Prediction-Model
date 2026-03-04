def test_snapshot_helper_compares_with_stable_order_and_float_tolerance(snapshot_assert) -> None:
    actual = {
        "b": [1, 2, 3],
        "a": {"y": 0.3000001, "x": "value"},
    }
    expected = {
        "a": {"x": "value", "y": 0.3},
        "b": [1, 2, 3],
    }

    snapshot_assert(actual, expected, float_tol=1e-3)
