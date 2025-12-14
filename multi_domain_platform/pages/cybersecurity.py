import streamlit as st
from services.database_manager import DatabaseManager
from models.security_incident import SecurityIncident

st.set_page_config(page_title="Cyber Security")

if "user" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

st.title("Cyber Security - Incidents")

db = DatabaseManager()

# Ensure incidents table exists
db.execute_query("""
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    description TEXT NOT NULL
)
""")

# ---- Add New Incident (do this BEFORE fetching so rerun shows new row immediately) ----
st.subheader("Add New Incident")

incident_type = st.text_input("Incident Type")
description = st.text_area("Description")
severity = st.selectbox("Severity", ["low", "medium", "high", "critical"])
status = st.selectbox("Status", ["Open", "Investigating", "Closed"])

if st.button("Add Incident"):
    if incident_type.strip() and description.strip():
        db.execute_query(
            "INSERT INTO incidents (incident_type, severity, status, description) VALUES (?, ?, ?, ?)",
            (incident_type.strip(), severity, status, description.strip()),
        )
        st.success("Incident added ✅")
        st.rerun()  # ✅ forces page refresh so the new incident appears
    else:
        st.error("Incident Type and Description cannot be empty.")

st.divider()

# ---- Existing Incidents ----
rows = db.fetch_all("SELECT id, incident_type, severity, status, description FROM incidents")
incidents = [SecurityIncident.from_row(r) for r in rows]

st.subheader("Existing Incidents")
if not incidents:
    st.info("No incidents yet.")
else:
    for inc in incidents:
        st.write(str(inc))



st.divider()
st.subheader("Incidents by Severity")

severity_rows = db.fetch_all("""
SELECT severity, COUNT(*) 
FROM incidents 
GROUP BY severity
""")

if severity_rows:
    labels = [r[0] for r in severity_rows]
    counts = [r[1] for r in severity_rows]
    st.bar_chart({"severity": counts}, x_label="Severity", y_label="Count")
else:
    st.info("No data for chart yet.")
