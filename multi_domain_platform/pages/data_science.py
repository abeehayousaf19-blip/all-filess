import streamlit as st
from services.database_manager import DatabaseManager
from models.dataset import Dataset

st.set_page_config(page_title="Data Science")

if "user" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

st.title("Data Science - Datasets")

db = DatabaseManager()

# Ensure datasets table exists
db.execute_query("""
CREATE TABLE IF NOT EXISTS datasets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    owner TEXT NOT NULL
)
""")

# Add Dataset
st.subheader("Add New Dataset")
name = st.text_input("Dataset Name")
owner = st.text_input("Owner")

if st.button("Add Dataset"):
    if name.strip() and owner.strip():
        db.execute_query(
            "INSERT INTO datasets (name, owner) VALUES (?, ?)",
            (name.strip(), owner.strip()),
        )
        st.success("Dataset added ✅")
        st.rerun()
    else:
        st.error("Dataset Name and Owner cannot be empty.")

st.divider()

# Existing Datasets
rows = db.fetch_all("SELECT id, name, owner FROM datasets")
datasets = [Dataset.from_row(r) for r in rows]

st.subheader("Existing Datasets")
if not datasets:
    st.info("No datasets yet.")
else:
    for d in datasets:
        st.write(str(d))
