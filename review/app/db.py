import os
import sqlite3
from collections.abc import Iterator

DB_PATH = os.environ.get("COHORT_DB", "cohorts.db")


def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
