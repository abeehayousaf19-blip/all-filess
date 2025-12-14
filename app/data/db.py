import sqlite3
from pathlib import Path

# Path to your database
DB_PATH = Path("DATA") / "intelligence_platform.db"

def connect_database():
    """Connect to the SQLite database and return the connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows you to access columns by name
    return conn

def create_users_table():
    """Create the users table if it doesn't exist."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()
