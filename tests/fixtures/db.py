from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TypeVar


T = TypeVar("T")


@dataclass
class SqliteEngine:
    db_path: Path
    disposed: bool = False

    def connect(self) -> sqlite3.Connection:
        if self.disposed:
            raise RuntimeError("engine is disposed")
        return sqlite3.connect(self.db_path)

    def dispose(self) -> None:
        self.disposed = True


@dataclass
class DbSessionManager:
    engine: SqliteEngine
    rollback_count: int = 0

    def run(self, operation: Callable[[sqlite3.Connection], T]) -> T:
        conn = self.engine.connect()
        conn.execute("BEGIN")
        try:
            result = operation(conn)
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            self.rollback_count += 1
            raise
        finally:
            conn.close()
