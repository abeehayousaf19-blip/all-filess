import os
import csv
import sqlite3
import bcrypt
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- Constants -----------------
DATA_FOLDER = 'DATA'
DB_FILE = os.path.join(DATA_FOLDER, 'intelligence_platform.db')

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# ---------------- Database -----------------
def connect_database():
    return sqlite3.connect(DB_FILE)

def create_users_table():
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_cyber_incidents_table():
    conn = connect_database()
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()

def create_intelligence_reports_table():
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intelligence_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

def create_security_threats_table():
    conn = connect_database()
    cursor = conn.cursor()
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

def create_it_tickets_table():
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS it_tickets(
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

# ---------------- CSV Loading -----------------
def load_users_csv(conn):
    filepath = os.path.join(DATA_FOLDER, "users.csv")
    if not os.path.exists(filepath):
        print("⚠ users.csv not found — skipping import")
        return
    conn.execute("DELETE FROM users")
    conn.commit()
    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            username = row.get("username")
            password = row.get("password")
            role = row.get("role", "user")
            if not username or not password:
                continue
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hashed, role)
            )
    conn.commit()

def load_csv_to_table(conn, filename, table, columns):
    filepath = os.path.join(DATA_FOLDER, filename)
    if not os.path.exists(filepath):
        print(f"⚠ {filename} not found — skipping import")
        return
    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            values = tuple(row.get(col) for col in columns)
            placeholders = ','.join('?' * len(columns))
            conn.execute(
                f"INSERT OR IGNORE INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
                values
            )
        conn.commit()

def load_all_csvs():
    conn = connect_database()
    load_users_csv(conn)
    load_csv_to_table(conn, 'cyber_incidents.csv', 'cyber_incidents',
                      ['date', 'incident_type', 'severity', 'status', 'description', 'reported_by'])
    load_csv_to_table(conn, 'intelligence_reports.csv', 'intelligence_reports',
                      ['title', 'description', 'date'])
    load_csv_to_table(conn, 'security_threats.csv', 'security_threats',
                      ['threat_name', 'severity', 'detected_on'])
    load_csv_to_table(conn, 'it_tickets.csv', 'it_tickets',
                      ['ticket_id','title','status','priority','assigned_to','created_on'])
    conn.close()

# ---------------- User Functions -----------------
def register_user(username, password, role='user'):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return False, f"Username '{username}' already exists."
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                   (username, hashed.decode('utf-8'), role))
    conn.commit()
    conn.close()
    return True, f"User '{username}' registered successfully!"

def login_user(username, password):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        return False, 'Username not found.'
    stored_hash = user[2]
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return True, f'Welcome, {username}!'
    else:
        return False, 'Invalid password.'

# ---------------- Fetch Data -----------------
def get_intelligence_reports(conn):
    return pd.read_sql_query("SELECT * FROM intelligence_reports", conn)

def get_security_threats(conn):
    return pd.read_sql_query("SELECT * FROM security_threats", conn)

def get_cyber_incidents(conn):
    return pd.read_sql_query("SELECT * FROM cyber_incidents", conn)

def get_users(conn):
    return pd.read_sql_query("SELECT * FROM users", conn)

def get_it_tickets(conn):
    return pd.read_sql_query("SELECT * FROM it_tickets", conn)

# ---------------- Streamlit UI -----------------
def run_streamlit_ui():
    st.set_page_config(page_title="Week-9 Dashboard", layout="wide")

    if "csv_loaded" not in st.session_state:
        load_all_csvs()
        st.session_state["csv_loaded"] = True

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.session_state.role = ''

    st.title("Intelligence Dashboard")

    if not st.session_state.logged_in:
        st.subheader("Register New User")
        reg_username = st.text_input("Username", key="reg_user")
        reg_password = st.text_input("Password", type="password", key="reg_pass")
        reg_role = st.selectbox("Role", ["user", "analyst", "admin"], key="reg_role")
        if st.button("Register"):
            success, msg = register_user(reg_username, reg_password, reg_role)
            if success:
                st.success(msg)
            else:
                st.error(msg)

        st.subheader("Login")
        login_username = st.text_input("Login Username", key="login_user")
        login_password = st.text_input("Login Password", type="password", key="login_pass")
        if st.button("Login"):
            success, msg = login_user(login_username, login_password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                conn = connect_database()
                role_df = pd.read_sql_query(
                    f"SELECT role FROM users WHERE username='{login_username}'", conn
                )
                st.session_state.role = role_df.iloc[0]['role']
                conn.close()
                st.rerun()
            else:
                st.error(msg)
    else:
        st.sidebar.title("Navigation")
        pages = ["Dashboard", "My Profile", "My Incidents"]
        if st.session_state.role == "admin":
            pages.append("Admin Panel")
        if st.session_state.role == "analyst":
            pages.append("Analyst Tools")
        page = st.sidebar.radio("Go to:", pages)
        st.sidebar.write("Logged in as:", st.session_state.username)
        st.sidebar.write("Role:", st.session_state.role)
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.rerun()

        conn = connect_database()

        # ---------------- Dashboard -----------------
        if page == "Dashboard":
            st.header(f"Welcome, {st.session_state.username}! 👋")
            st.subheader("Your Personalized Dashboard")

            # Cyber Incidents
            incidents = get_cyber_incidents(conn)
            my_incidents = incidents[incidents["reported_by"] == st.session_state.username]
            col1, col2 = st.columns(2)
            col1.metric("Total Incidents Reported", len(my_incidents))
            col2.metric("Open Incidents", len(my_incidents[my_incidents["status"] == "Open"]))

            if not my_incidents.empty:
                my_incidents['date'] = pd.to_datetime(my_incidents['date'], errors='coerce')
                my_incidents = my_incidents.dropna(subset=['date'])
                if not my_incidents.empty:
                    my_incidents['date_only'] = my_incidents['date'].dt.date
                    incidents_over_time = my_incidents.groupby('date_only').size().reset_index(name='count')
                    st.subheader("Your Incident Trend Over Time")
                    fig_incidents = px.line(
                        incidents_over_time, 
                        x='date_only', y='count', 
                        markers=True, 
                        title="Your Incidents Over Time"
                    )
                    st.plotly_chart(fig_incidents)
                    st.subheader("Incident Severity Distribution")
                    st.bar_chart(my_incidents['severity'].value_counts())
                else:
                    st.info("You have no valid incident dates to display.")
            else:
                st.info("You have no incidents reported.")

            # IT Tickets
            st.write("---")
            st.subheader("IT Tickets Overview")
            tickets = get_it_tickets(conn)
            if not tickets.empty:
                tickets['created_on'] = pd.to_datetime(tickets['created_on'], errors='coerce')
                tickets = tickets.dropna(subset=['created_on'])
                if not tickets.empty:
                    tickets['date_only'] = tickets['created_on'].dt.date
                    tickets_over_time = tickets.groupby('date_only').size().reset_index(name='count')
                    col3, col4 = st.columns(2)
                    col3.metric("Total Tickets", len(tickets))
                    col4.metric("Open Tickets", len(tickets[tickets["status"]=="Open"]))
                    st.subheader("Ticket Trend Over Time")
                    fig_tickets = px.line(
                        tickets_over_time, 
                        x='date_only', y='count', 
                        markers=True, 
                        title="IT Tickets Over Time"
                    )
                    st.plotly_chart(fig_tickets)
                    st.subheader("Ticket Status Distribution")
                    st.bar_chart(tickets['status'].value_counts())
                    st.subheader("Ticket Priority Distribution")
                    st.bar_chart(tickets['priority'].value_counts())
                else:
                    st.info("No valid ticket dates to display.")
            else:
                st.info("No IT tickets recorded yet.")

        # ---------------- My Profile -----------------
        elif page == "My Profile":
            st.header("My Profile")
            st.write("Username:", st.session_state.username)
            st.write("Role:", st.session_state.role)

        # ---------------- My Incidents -----------------
        elif page == "My Incidents":
            st.header("My Incidents")
            incidents = get_cyber_incidents(conn)
            my_incidents = incidents[incidents["reported_by"] == st.session_state.username]
            st.dataframe(my_incidents)

        # ---------------- Admin Panel -----------------
        elif page == "Admin Panel":
            st.header("Admin Panel (Admins Only)")
            users_df = get_users(conn)
            st.dataframe(users_df)

        # ---------------- Analyst Tools -----------------
        elif page == "Analyst Tools":
            st.header("Analyst Tools")
            incidents = get_cyber_incidents(conn)
            if not incidents.empty:
                incidents['date'] = pd.to_datetime(incidents['date'], errors='coerce')
                incidents = incidents.dropna(subset=['date'])
                if not incidents.empty:
                    incidents['date_only'] = incidents['date'].dt.date
                    incidents_over_time = incidents.groupby('date_only').size().reset_index(name='count')
                    fig1 = px.line(
                        incidents_over_time, 
                        x='date_only', y='count', 
                        markers=True, 
                        title='All Incidents Over Time'
                    )
                    st.plotly_chart(fig1)
                    st.subheader("Incident Severity Distribution")
                    st.bar_chart(incidents['severity'].value_counts())
            else:
                st.info("No incidents yet.")

            reports = get_intelligence_reports(conn)
            st.subheader("Intelligence Reports")
            if reports.empty:
                st.info("No intelligence reports yet.")
            else:
                st.dataframe(reports)

            threats = get_security_threats(conn)
            st.subheader("Security Threats")
            if threats.empty:
                st.info("No security threats recorded yet.")
            else:
                st.dataframe(threats)

            tickets = get_it_tickets(conn)
            st.subheader("IT Tickets Overview")
            if not tickets.empty:
                tickets['created_on'] = pd.to_datetime(tickets['created_on'], errors='coerce')
                tickets = tickets.dropna(subset=['created_on'])
                if not tickets.empty:
                    tickets['date_only'] = tickets['created_on'].dt.date
                    tickets_over_time = tickets.groupby('date_only').size().reset_index(name='count')
                    fig2 = px.line(
                        tickets_over_time, 
                        x='date_only', y='count', 
                        markers=True, 
                        title='IT Tickets Over Time'
                    )
                    st.plotly_chart(fig2)
                    st.bar_chart(tickets['status'].value_counts())
                    st.bar_chart(tickets['priority'].value_counts())
            else:
                st.info("No IT tickets recorded yet.")

        conn.close()

# ---------------- Main -----------------
def main():
    create_users_table()
    create_cyber_incidents_table()
    create_intelligence_reports_table()
    create_security_threats_table()
    create_it_tickets_table()
    run_streamlit_ui()

if __name__ == "__main__":
    main()