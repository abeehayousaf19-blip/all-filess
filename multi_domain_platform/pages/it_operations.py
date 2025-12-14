import streamlit as st
from services.database_manager import DatabaseManager
from models.it_ticket import ITTicket

st.set_page_config(page_title="IT Operations")

if "user" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

st.title("IT Operations - Tickets")

db = DatabaseManager()

# Ensure tickets table exists
db.execute_query("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    status TEXT NOT NULL
)
""")

# Add Ticket
st.subheader("Add New Ticket")
subject = st.text_input("Subject")
status = st.selectbox("Status", ["Open", "In Progress", "Closed"])

if st.button("Add Ticket"):
    if subject.strip():
        db.execute_query(
            "INSERT INTO tickets (subject, status) VALUES (?, ?)",
            (subject.strip(), status),
        )
        st.success("Ticket added ✅")
        st.rerun()
    else:
        st.error("Subject cannot be empty.")

st.divider()

# Existing Tickets
rows = db.fetch_all("SELECT id, subject, status FROM tickets")
tickets = [ITTicket.from_row(r) for r in rows]

st.subheader("Existing Tickets")
if not tickets:
    st.info("No tickets yet.")
else:
    for t in tickets:
        st.write(str(t))

# Chart: Tickets by Status
st.divider()
st.subheader("Tickets by Status")

status_rows = db.fetch_all("""
SELECT status, COUNT(*)
FROM tickets
GROUP BY status
""")

if status_rows:
    chart_data = {r[0]: r[1] for r in status_rows}
    st.bar_chart(chart_data)
else:
    st.info("No data for chart yet.")
