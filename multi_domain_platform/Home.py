import streamlit as st

from services.database_manager import DatabaseManager
from database.setup import init_db

db = DatabaseManager()
init_db(db)

st.set_page_config(page_title="Multi Domain Platform", layout="wide")
st.title("Multi Domain Platform")

st.write("Use the sidebar to navigate to the pages.")
