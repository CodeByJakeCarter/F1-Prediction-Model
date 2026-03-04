import pytest


def test_db_session_rolls_back_on_error(db_engine, db_session) -> None:
    setup_connection = db_engine.connect()
    setup_connection.execute(
        "CREATE TABLE results (id INTEGER PRIMARY KEY AUTOINCREMENT, value TEXT NOT NULL)"
    )
    setup_connection.commit()
    setup_connection.close()

    def failing_operation(connection) -> None:
        connection.execute("INSERT INTO results (value) VALUES (?)", ("before-error",))
        raise RuntimeError("force rollback")

    with pytest.raises(RuntimeError):
        db_session.run(failing_operation)

    verify_connection = db_engine.connect()
    count = verify_connection.execute("SELECT COUNT(*) FROM results").fetchone()[0]
    verify_connection.close()

    assert count == 0
    assert db_session.rollback_count == 1
