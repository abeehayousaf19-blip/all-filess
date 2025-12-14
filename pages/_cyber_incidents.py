import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime, timedelta
import random

# -----------------------------
# File Path
# -----------------------------
FILE_PATH = r"C:\Users\Huzi\OneDrive\Documents\M01088971_LABFILES\DATA\cyber_incidents.csv"

# Ensure folder exists
os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)

# -----------------------------
# Generate sample data if CSV missing
# -----------------------------
if not os.path.exists(FILE_PATH):
    incident_types = ["Phishing", "Malware", "Data Breach", "DDoS", "Insider Threat"]
    severities = ["Low", "Medium", "High", "Critical"]
    statuses = ["Open", "In Progress", "Resolved"]
    reporters = ["Alice", "Bob", "Charlie", "David", "Eve"]

    sample_data = []
    start_date = datetime(2025, 12, 1)

    for i in range(50):
        date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        incident_type = random.choice(incident_types)
        severity = random.choice(severities)
        status = random.choice(statuses)
        description = f"{incident_type} detected, severity {severity}"
        reported_by = random.choice(reporters)
        sample_data.append([date, incident_type, severity, status, description, reported_by])

    df = pd.DataFrame(sample_data, columns=["date","incident_type","severity","status","description","reported_by"])
    df.to_csv(FILE_PATH, index=False)
else:
    df = pd.read_csv(FILE_PATH)

# -----------------------------
# Streamlit App
# -----------------------------
st.title("📄 Cyber Incidents Dashboard")
st.write("Manage and visualize cyber incidents easily.")

# --- ADD INCIDENT ---
with st.expander("➕ Add New Incident"):
    with st.form("add_incident"):
        date = st.date_input("Date")
        incident_type = st.text_input("Incident Type")
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
        description = st.text_area("Description")
        reported_by = st.text_input("Reported By")
        submitted = st.form_submit_button("Add Incident")
        if submitted:
            new_row = pd.DataFrame({
                "date": [date],
                "incident_type": [incident_type],
                "severity": [severity],
                "status": [status],
                "description": [description],
                "reported_by": [reported_by]
            })
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(FILE_PATH, index=False)
            st.success("Incident added successfully!")
            st.rerun()

# --- UPDATE INCIDENT ---
with st.expander("✏️ Update Incident"):
    if not df.empty:
        update_index = st.number_input("Row Number to Update", 0, len(df)-1, 0)
        if st.button("Load Incident for Update"):
            row = df.iloc[update_index]
            date = st.date_input("Date", pd.to_datetime(row['date']))
            incident_type = st.text_input("Incident Type", row['incident_type'])
            severity = st.selectbox("Severity", ["Low","Medium","High","Critical"], 
                                    index=["Low","Medium","High","Critical"].index(row['severity']))
            status = st.selectbox("Status", ["Open","In Progress","Resolved"], 
                                  index=["Open","In Progress","Resolved"].index(row['status']))
            description = st.text_area("Description", row['description'])
            reported_by = st.text_input("Reported By", row['reported_by'])
            if st.button("Update Incident"):
                df.at[update_index,'date'] = date
                df.at[update_index,'incident_type'] = incident_type
                df.at[update_index,'severity'] = severity
                df.at[update_index,'status'] = status
                df.at[update_index,'description'] = description
                df.at[update_index,'reported_by'] = reported_by
                df.to_csv(FILE_PATH, index=False)
                st.success("Incident updated!")
                st.rerun()

# --- DELETE INCIDENT ---
with st.expander("🗑️ Delete Incident"):
    if not df.empty:
        delete_index = st.number_input("Row Number to Delete", 0, len(df)-1, 0, key="del_index")
        if st.button("Delete Incident"):
            df = df.drop(delete_index).reset_index(drop=True)
            df.to_csv(FILE_PATH, index=False)
            st.success("Incident deleted!")
            st.rerun()

# --- AI Assistant ---
with st.expander("🤖 AI Assistant"):
    query = st.text_input("Ask about Cyber Incidents", key="ai_query")
    if st.button("Get Answer"):
        filtered = df[df.apply(lambda row: query.lower() in str(row).lower(), axis=1)]
        if not filtered.empty:
            st.dataframe(filtered, use_container_width=True)
        else:
            st.write("No matching incidents found.")

# --- Graphs ---
if not df.empty:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Incidents Over Time
    st.subheader("📈 Incidents Over Time")
    timeline = df.groupby('date').size().reset_index(name='Count')
    fig_time = px.line(timeline, x='date', y='Count', markers=True, title="Incidents Over Time")
    st.plotly_chart(fig_time, use_container_width=True)

    # Incidents by Severity
    st.subheader("🛑 Incidents by Severity")
    severity_count = df['severity'].value_counts().reset_index()
    severity_count.columns = ['Severity','Count']
    fig_sev = px.bar(severity_count, x='Severity', y='Count', color='Severity', text='Count', title="Incidents by Severity")
    st.plotly_chart(fig_sev, use_container_width=True)

    # Incidents by Type
    st.subheader("🔹 Incidents by Type")
    type_count = df['incident_type'].value_counts().reset_index()
    type_count.columns = ['Type','Count']
    fig_type = px.pie(type_count, names='Type', values='Count', title="Incidents by Type")
    st.plotly_chart(fig_type, use_container_width=True)

# --- Show Data Table ---
st.header("📊 All Cyber Incidents")
st.dataframe(df, use_container_width=True)
