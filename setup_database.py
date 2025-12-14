import os
import csv
import sqlite3
import bcrypt

# ---------------- Constants -----------------
DATA_FOLDER = "DATA"
DB_FILE = "intelligence_platform.db"

# ---------------- Database -----------------
def connect_db():
    return sqlite3.connect(DB_FILE)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            incident_type TEXT,
            severity TEXT,
            status TEXT,
            description TEXT,
            reported_by TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intelligence_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_threats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            threat_name TEXT,
            severity TEXT,
            detected_on TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- Load CSVs -----------------
def normalize_header(header):
    """Normalize header names to lowercase and replace spaces with underscores"""
    return header.strip().lower().replace(" ", "_")

def load_users_csv(conn):
    filepath = os.path.join(DATA_FOLDER, "users.csv")
    if not os.path.exists(filepath):
        print("⚠ users.csv not found — skipping import")
        return
    
    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        # Normalize CSV headers
        reader.fieldnames = [normalize_header(h) for h in reader.fieldnames]
        inserted = 0
        for row in reader:
            try:
                username = row.get("username")
                password = row.get("password")
                role = row.get("role")
                if not username or not password or not role:
                    print(f"⚠ Skipping row with missing data: {row}")
                    continue

                hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                conn.execute(
                    "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, hashed, role)
                )
                inserted += 1
            except Exception as e:
                print("Error inserting user:", e)

        conn.commit()
        print(f"✓ Imported {inserted} users")


def load_csv_generic(conn, filename, table, expected_columns):
    """
    Generic CSV loader:
    - Normalizes CSV headers
    - Maps columns even if capitalization/spaces differ
    """
    path = os.path.join(DATA_FOLDER, filename)
    if not os.path.exists(path):
        print(f"⚠ {filename} missing — skipping import")
        return
    
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        # Normalize CSV headers
        normalized_headers = [normalize_header(h) for h in reader.fieldnames]
        column_map = {}
        for col in expected_columns:
            try:
                idx = normalized_headers.index(normalize_header(col))
                column_map[col] = reader.fieldnames[idx]  # map expected -> actual header
            except ValueError:
                print(f"⚠ Column '{col}' not found in {filename}")
                column_map[col] = None

        count = 0
        for row in reader:
            try:
                values = []
                skip_row = False
                for col in expected_columns:
                    actual_col = column_map.get(col)
                    if actual_col is None:
                        values.append(None)
                    else:
                        values.append(row.get(actual_col))
                conn.execute(
                    f"INSERT OR IGNORE INTO {table} ({','.join(expected_columns)}) VALUES ({','.join(['?']*len(expected_columns))})",
                    tuple(values)
                )
                count += 1
            except Exception as e:
                print("Error:", e)
        conn.commit()
        print(f"✓ Imported {count} → {table}")


# ---------------- Main -----------------
if __name__ == "__main__":
    print("\n🚀 SETTING UP DATABASE\n")
    create_tables()
    conn = connect_db()

    # Users
    load_users_csv(conn)

    # Cyber incidents
    load_csv_generic(
        conn,
        "cyber_incidents.csv",
        "cyber_incidents",
        ["date", "incident_type", "severity", "status", "description", "reported_by"]
    )

    # Intelligence reports
    load_csv_generic(
        conn,
        "intelligence_reports.csv",
        "intelligence_reports",
        ["title", "description", "date"]
    )

    # Security threats
    load_csv_generic(
        conn,
        "security_threats.csv",
        "security_threats",
        ["threat_name", "severity", "detected_on"]
    )

    conn.close()
    print("\n🎉 DATABASE SETUP COMPLETE!")
