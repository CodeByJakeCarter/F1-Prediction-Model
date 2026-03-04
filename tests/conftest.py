from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.main import healthcheck
from fixtures.db import DbSessionManager, SqliteEngine
from fixtures.factories import EntityFactory
from fixtures.http import SimpleASGIClient
from fixtures.snapshot import assert_snapshot_like


@pytest.fixture
def tmp_artifacts_dir(tmp_path: Path) -> Path:
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()
    return artifacts_dir


@pytest.fixture
def db_engine(tmp_artifacts_dir: Path) -> SqliteEngine:
    engine = SqliteEngine(db_path=tmp_artifacts_dir / "test.sqlite3")
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine: SqliteEngine) -> DbSessionManager:
    return DbSessionManager(engine=db_engine)


@pytest.fixture
def entity_factory() -> EntityFactory:
    return EntityFactory()


@pytest.fixture
def http_client() -> SimpleASGIClient:
    return SimpleASGIClient(healthcheck)


@pytest.fixture
def fixed_now() -> datetime:
    return datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def snapshot_assert():
    return assert_snapshot_like
