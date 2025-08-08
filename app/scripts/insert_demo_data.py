import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DB_PATH = os.path.join(BASE_DIR, "data", "demo.sqlite")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Connect to SQLite
print(os.path.abspath(DB_PATH))
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    record_id INTEGER,
    name TEXT,
    email TEXT,
    status TEXT
)
""")

# Sample data
records = [
    (114, "John Doe", "john@example.com", "active"),
    (115, "Jane Doe", "jane@example.com", "active"),
    (116, "Alice Smith", "alice@example.com", "active")
]

# Insert only if not already in table
for rec in records:
    query = "INSERT OR IGNORE INTO users (record_id, name, email, status) VALUES (?, ?, ?, ?)"
    cursor.execute(
        "INSERT OR IGNORE INTO users (record_id, name, email, status) VALUES (?, ?, ?, ?)",
        rec
    )

conn.commit()
conn.close()

print(f"✅ Demo data inserted into {DB_PATH}")
