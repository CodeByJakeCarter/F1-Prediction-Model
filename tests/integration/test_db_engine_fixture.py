def test_db_engine_fixture_creates_and_disposes_connection(db_engine) -> None:
    connection = db_engine.connect()
    connection.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY, value TEXT)")
    connection.close()

    db_engine.dispose()
    assert db_engine.disposed is True
