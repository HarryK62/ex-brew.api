import sqlite3

import pytest

from app import customers
from app.customers import lookup_customer


@pytest.fixture
def db(tmp_path, monkeypatch):
    path = tmp_path / "customers.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    conn.executemany(
        "INSERT INTO customers (name, email) VALUES (?, ?)",
        [("Ada", "ada@example.com"), ("Grace", "grace@example.com")],
    )
    conn.commit()
    conn.close()
    monkeypatch.setattr(customers, "DB_PATH", path)
    return path


def test_lookup_finds_customer(db):
    assert lookup_customer("Ada") == {"id": 1, "name": "Ada", "email": "ada@example.com"}


def test_lookup_missing_returns_none(db):
    assert lookup_customer("Nobody") is None


def test_sql_injection_is_treated_as_a_name(db):
    # With the old f-string query this matched every row.
    assert lookup_customer("x' OR '1'='1") is None


def test_connection_is_closed(db, monkeypatch):
    opened = []
    real_connect = sqlite3.connect

    def tracking_connect(*args, **kwargs):
        conn = real_connect(*args, **kwargs)
        opened.append(conn)
        return conn

    monkeypatch.setattr(customers.sqlite3, "connect", tracking_connect)
    lookup_customer("Ada")
    with pytest.raises(sqlite3.ProgrammingError):
        opened[0].execute("SELECT 1")  # fails only on a closed connection


def test_lookup_result_has_no_api_key(db, monkeypatch):
    monkeypatch.setenv("BREW_API_KEY", "test-key")
    result = lookup_customer("Ada")
    assert set(result) == {"id", "name", "email"}
    assert "test-key" not in str(result)
