"""Customer lookup."""
import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "customers.db"


def lookup_customer(name: str, db_path: Path | None = None) -> dict | None:
    """Return the customer with this name, or None if there isn't one."""
    db_path = db_path or DB_PATH
    # closing() makes sure the connection is closed even if the query raises.
    # (A bare `with sqlite3.connect(...)` only commits/rolls back; it doesn't close.)
    with closing(sqlite3.connect(db_path)) as conn:
        # The ? placeholder sends `name` as data, so it can never change the SQL.
        row = conn.execute(
            "SELECT id, name, email FROM customers WHERE name = ?", (name,)
        ).fetchone()
    if row is None:
        return None
    return {"id": row[0], "name": row[1], "email": row[2]}
