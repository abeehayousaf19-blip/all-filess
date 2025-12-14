import streamlit as st
import pandas as pd
import os

# ----------------------------------------
# FIXED: Correct file path for YOUR system
# ----------------------------------------
FILE_PATH = r"C:\Users\Huzi\OneDrive\Documents\M01088971_LABFILES\DATA\security_threats.csv"

# Create folder if missing
os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)

# Create empty CSV if not exists
if not os.path.exists(FILE_PATH):
    empty_df = pd.DataFrame(columns=["Threat Name", "Type", "Description", "Status"])
    empty_df.to_csv(FILE_PATH, index=False)

df = pd.read_csv(FILE_PATH)

st.title("🛡️ Security Threats")
st.write("Manage security threats using the forms below.")

# --- ADD THREAT ---
with st.expander("➕ Add New Threat"):
    with st.form("add_threat"):
        name = st.text_input("Threat Name")
        threat_type = st.text_input("Type")
        description = st.text_area("Description")
        status = st.selectbox("Status", ["Active", "Mitigated", "Resolved"])
        submitted = st.form_submit_button("Add Threat")
        if submitted:
            new_row = pd.DataFrame({
                "Threat Name": [name],
                "Type": [threat_type],
                "Description": [description],
                "Status": [status]
            })
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(FILE_PATH, index=False)
            st.success("Threat added successfully!")
            st.rerun()

# --- UPDATE THREAT ---
with st.expander("✏️ Update Threat"):
    update_index = st.number_input("Row Number to Update", 0, len(df)-1, 0)
    if st.button("Load Threat for Update"):
        row = df.iloc[update_index]
        name = st.text_input("Threat Name", row['Threat Name'])
        threat_type = st.text_input("Type", row['Type'])
        description = st.text_area("Description", row['Description'])
        status = st.selectbox(
            "Status",
            ["Active", "Mitigated", "Resolved"],
            index=["Active", "Mitigated", "Resolved"].index(row['Status'])
        )
        if st.button("Update Threat"):
            df.at[update_index, 'Threat Name'] = name
            df.at[update_index, 'Type'] = threat_type
            df.at[update_index, 'Description'] = description
            df.at[update_index, 'Status'] = status
            df.to_csv(FILE_PATH, index=False)
            st.success("Threat updated!")
            st.rerun()

# --- DELETE THREAT ---
with st.expander("🗑️ Delete Threat"):
    delete_index = st.number_input("Row Number to Delete", 0, len(df)-1, 0, key="del_index2")
    if st.button("Delete Threat"):
        df = df.drop(delete_index).reset_index(drop=True)
        df.to_csv(FILE_PATH, index=False)
        st.success("Threat deleted!")
        st.rerun()

# --- AI ASSISTANT ---
with st.expander("🤖 AI Assistant"):
    query = st.text_input("Ask about Security Threats", key="ai_query2")
    if st.button("Get Answer"):
        filtered = df[df.apply(lambda row: query.lower() in str(row).lower(), axis=1)]
        if not filtered.empty:
            st.dataframe(filtered, use_container_width=True)
        else:
            st.write("No matching threats found.")

# --- SHOW DATA TABLE ---
st.header("📊 All Security Threats")
st.dataframe(df, use_container_width=True)
