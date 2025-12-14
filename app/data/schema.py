import sqlite3
import os
import csv
import bcrypt

# Path to the main DB file
DB_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "DATA", "intelligence_platform.db")
DB_FILE = os.path.abspath(DB_FILE)

def connect():
    """Connect to SQLite database."""
    return sqlite3.connect(DB_FILE)

def create_tables():
    """Create all required tables."""
    conn = connect()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Cyber Incidents Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            incident_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            description TEXT NOT NULL,
            reported_by TEXT
        )
    """)

    # Intelligence Reports Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intelligence_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            date TEXT
        )
    """)

    # Security Threats Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_threats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            threat_name TEXT NOT NULL,
            severity TEXT,
            detected_on TEXT
        )
    """)

    # IT Tickets Table (matches your CSV columns)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS it_tickets (
            ticket_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT,
            assigned_to TEXT,
            created_on TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Tables created successfully.")

def load_users_from_csv():
    """Load users into DB from DATA/users.csv and hash passwords."""
    csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "DATA", "users.csv")
    csv_path = os.path.abspath(csv_path)

    if not os.path.exists(csv_path):
        print("users.csv not found. Skipping user import.")
        return

    conn = connect()
    cursor = conn.cursor()

    with open(csv_path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                # Hash the plain password
                hashed = bcrypt.hashpw(row["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                cursor.execute("""
                    INSERT OR IGNORE INTO users (username, password_hash, role)
                    VALUES (?, ?, ?)
                """, (row["username"], hashed, row["role"]))
                if cursor.rowcount == 0:
                    print(f"Skipped duplicate user: {row['username']}")
            except Exception as e:
                print("Error inserting user:", e)

    conn.commit()
    conn.close()
    print("Users imported from CSV.")

def load_it_tickets_csv():
    """Load IT tickets from CSV."""
    csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "DATA", "it_tickets.csv")
    csv_path = os.path.abspath(csv_path)

    if not os.path.exists(csv_path):
        print("⚠ it_tickets.csv not found — skipping import")
        return

    conn = connect()
    cursor = conn.cursor()

    with open(csv_path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO it_tickets
                    (ticket_id, title, status, priority, assigned_to, created_on)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    row["ticket_id"],
                    row["title"],
                    row["status"],
                    row.get("priority", ""),
                    row.get("assigned_to", ""),
                    row.get("created_on", "")
                ))
            except Exception as e:
                print(f"Failed to insert ticket {row}: {e}")

    conn.commit()
    conn.close()
    print("IT tickets imported from CSV.")

def run_all_migrations():
    """Run all migrations: create tables + load CSVs."""
    create_tables()
    load_users_from_csv()
    load_it_tickets_csv()
    print("All migrations completed.")

if __name__ == "__main__":
    run_all_migrations()
