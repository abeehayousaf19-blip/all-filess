import os
import sqlite3

# ---------------- Database -----------------
# Database path relative to this script
DB_FILE = os.path.join(os.path.dirname(__file__), "..", "intelligence_platform.db")

def connect_database():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    return conn

def fetch_all_users():
    """Fetch all users from the database."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

# ---------------- Export -----------------
def export_users_to_file(output_path=None):
    """
    Export users to a Python file.
    If output_path is None, defaults to 'users_exported.py' in the same folder.
    """
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "users_exported.py")
    
    users = fetch_all_users()
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("import sqlite3\n\n")
        f.write("# Auto-generated file containing all users from the database\n\n")
        f.write("users_data = [\n")
        for user in users:
            user_id, username, password_hash, role = user
            f.write(
                f"    {{'id': {user_id}, 'username': '{username}', "
                f"'password_hash': '{password_hash}', 'role': '{role}'}},\n"
            )
        f.write("]\n\n")
        f.write("print('Loaded users:', users_data)\n")
    
    print(f"Users exported successfully to {output_path}")

# ---------------- Main -----------------
if __name__ == "__main__":
    export_users_to_file()  # Will export to users_exported.py in the same folder
