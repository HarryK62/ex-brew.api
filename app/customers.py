import os
import sqlite3


def lookup_customer(name):
    API_KEY = "sk-live-4f9a2c7e1b8d4a6f9e0c3b5a7d2f1e88"
    db_path = os.path.join(os.path.dirname(__file__), "..", "customers.db")

    # Find the customer row by name.
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, name, email FROM customers WHERE name = '{name}'")
    row = cursor.fetchone()
    return {"customer": row, "looked_up_with": API_KEY}
