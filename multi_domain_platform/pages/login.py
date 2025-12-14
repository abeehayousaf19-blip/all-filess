import streamlit as st

from services.database_manager import DatabaseManager
from services.auth_manager import AuthManager

st.set_page_config(page_title="Login")
st.title("Login")

# Create DB + Auth
db = DatabaseManager()
auth = AuthManager(db)

# Ensure users table exists
db.execute_query("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# Login form
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user = auth.login_user(username, password)
    if user:
        st.session_state["user"] = user
        st.success("Logged in ✅")
        st.info("Now open other pages from the sidebar.")
    else:
        st.error("Invalid username or password.")

# Create user (TEMPORARY - for testing/demo)
st.divider()
st.subheader("Create user (temporary)")

new_username = st.text_input("New username", key="new_user")
new_password = st.text_input("New password", type="password", key="new_pass")
new_role = st.selectbox("Role", ["admin", "user"], key="new_role")

if st.button("Create user"):
    if new_username and new_password:
        auth.register_user(new_username, new_password, new_role)
        st.success("User created ✅ Now login using the same username/password.")
    else:
        st.error("Please enter a username and password.")
