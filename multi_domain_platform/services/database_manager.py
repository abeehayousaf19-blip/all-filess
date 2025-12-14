import sqlite3
from typing import Any, Iterable, Optional


class DatabaseManager:
    """Handles SQLite database connections and queries."""

    def __init__(self, db_path: str = "database/platform.db"):
        # Default path works when you run streamlit from multi_domain_platform/
        self._db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        # Open a fresh connection per operation (simple + reliable for Streamlit)
        return sqlite3.connect(self._db_path)

    def execute_query(self, sql: str, params: Iterable[Any] = ()) -> None:
        """Execute a write query (INSERT, UPDATE, DELETE)."""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, tuple(params))
            conn.commit()

    def fetch_one(self, sql: str, params: Iterable[Any] = ()) -> Optional[tuple]:
        """Fetch a single row."""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, tuple(params))
            return cur.fetchone()

    def fetch_all(self, sql: str, params: Iterable[Any] = ()) -> list[tuple]:
        """Fetch all rows."""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, tuple(params))
            return cur.fetchall()
