import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# ----------------------------------------
# File path for CSV
# ----------------------------------------
FILE_PATH = r"C:\Users\Huzi\OneDrive\Documents\M01088971_LABFILES\DATA\it_tickets.csv"

# Ensure folder exists
os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)

# Create empty CSV with default columns if it doesn't exist
default_columns = ["Subject", "Issue", "Priority", "Status", "Created By", "Created On", "Resolved On", "Assigned To"]
if not os.path.exists(FILE_PATH):
    empty_df = pd.DataFrame(columns=default_columns)
    empty_df.to_csv(FILE_PATH, index=False)

# Load CSV
df = pd.read_csv(FILE_PATH)

# Strip whitespace from columns
df.columns = df.columns.str.strip()

# Add missing columns if necessary
for col in default_columns:
    if col not in df.columns:
        df[col] = ""

# If CSV is empty, add realistic sample data for better visualization
if df.empty:
    np.random.seed(42)
    dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
    sample_data = []
    
    subjects = [
        "Login Issues", "Server Down", "Slow Performance", "Network Connection",
        "Software Installation", "Email Problems", "Printer Not Working",
        "Password Reset", "VPN Access", "Database Error", "Application Crash",
        "Internet Outage", "Hardware Failure", "Security Alert", "File Access"
    ]
    
    assigned_to_list = ["Tech-A", "Tech-B", "Tech-C", "Tech-D", "Tech-E"]
    
    for _ in range(50):  # Create 50 sample tickets
        created_date = np.random.choice(dates)
        priority = np.random.choice(["Low", "Medium", "High", "Critical"], p=[0.3, 0.4, 0.2, 0.1])
        status = np.random.choice(["Open", "In Progress", "Closed"], p=[0.2, 0.3, 0.5])
        
        # Add resolved date for closed tickets
        resolved_date = ""
        if status == "Closed":
            resolved_date = created_date + timedelta(hours=np.random.randint(1, 72))
        
        sample_data.append({
            "Subject": np.random.choice(subjects),
            "Issue": "Sample issue description",
            "Priority": priority,
            "Status": status,
            "Created By": np.random.choice(["John", "Sarah", "Mike", "Emma", "Admin"]),
            "Created On": created_date,
            "Resolved On": resolved_date,
            "Assigned To": np.random.choice(assigned_to_list)
        })
    
    df = pd.DataFrame(sample_data)
    df.to_csv(FILE_PATH, index=False)

# ----------------------------------------
# Helper Functions
# ----------------------------------------
def calculate_avg_response_time(df, threshold_minutes=60):
    """Calculate average response time for tickets resolved within threshold"""
    if df.empty:
        return 0
    
    df_copy = df.copy()
    df_copy['Created On'] = pd.to_datetime(df_copy['Created On'], errors='coerce')
    df_copy['Resolved On'] = pd.to_datetime(df_copy['Resolved On'], errors='coerce')
    
    resolved = df_copy.dropna(subset=['Resolved On'])
    if resolved.empty:
        return 0
    
    response_minutes = (resolved['Resolved On'] - resolved['Created On']).dt.total_seconds() / 60
    fast_tickets = response_minutes[response_minutes <= threshold_minutes]
    
    if fast_tickets.empty:
        return 0
    
    avg_fast = fast_tickets.mean()
    return round(avg_fast, 1)

def calculate_system_load(df):
    """Calculate daily ticket load"""
    if df.empty:
        return pd.DataFrame({"Date": [], "Tickets": []})
    
    df_copy = df.copy()
    df_copy['Created On'] = pd.to_datetime(df_copy['Created On'], errors='coerce')
    load = df_copy.groupby(df_copy['Created On'].dt.date).size().reset_index(name='Tickets')
    load.columns = ['Date', 'Tickets']
    load = load.sort_values('Date')
    return load

# ----------------------------------------
# Main Dashboard
# ----------------------------------------
st.title("💻 IT Tickets Dashboard")
st.write("Comprehensive IT ticket management and analytics")

# Create tabs for better organization
tab1, tab2 = st.tabs(["📊 Overview", "🎫 Manage Tickets"])

# ----------------------------------------
# TAB 1: OVERVIEW
# ----------------------------------------
with tab1:
    # Convert Created On to datetime
    if 'Created On' in df.columns:
        df['Created On'] = pd.to_datetime(df['Created On'], errors='coerce')
    
    # Calculate metrics
    total_tickets = len(df)
    avg_response_time = calculate_avg_response_time(df)
    servers_online = df['Assigned To'].nunique() if 'Assigned To' in df.columns else 0
    
    st.header("💻 IT Overview")
    
    # Top metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tickets", total_tickets)
    with col2:
        st.metric("Servers Online", servers_online)
    with col3:
        st.metric("Avg Response Time (min)", avg_response_time)
    
    # Additional metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        open_tickets = len(df[df['Status'] == 'Open'])
        st.metric("Open Tickets", open_tickets)
    with col2:
        in_progress = len(df[df['Status'] == 'In Progress'])
        st.metric("In Progress", in_progress)
    with col3:
        if not df.empty:
            critical_tickets = len(df[df['Priority'] == 'Critical'])
            st.metric("Critical", critical_tickets)
    with col4:
        if 'Created On' in df.columns and not df['Created On'].isna().all():
            today = pd.Timestamp.now().date()
            today_tickets = len(df[df['Created On'].dt.date == today])
            st.metric("Today", today_tickets)
    
    # System Load Line Chart
    st.subheader("System Load (Tickets per Day)")
    system_load_df = calculate_system_load(df)
    if not system_load_df.empty:
        fig_load = px.line(
            system_load_df,
            x='Date',
            y='Tickets',
            markers=True,
            line_shape='spline'
        )
        fig_load.update_traces(
            line=dict(color='#6366f1', width=3),
            marker=dict(size=8, color='#ef4444', line=dict(width=2, color='white'))
        )
        fig_load.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Tickets",
            hovermode='x unified',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(gridcolor='rgba(200,200,200,0.2)')
        )
        st.plotly_chart(fig_load, use_container_width=True)
    
    # Status and Priority Charts
    st.subheader("📊 Ticket Analytics")
    col1, col2 = st.columns(2)
    
    with col1:
        # Status Distribution
        if 'Status' in df.columns and not df.empty:
            status_count = df['Status'].value_counts().reset_index()
            status_count.columns = ['Status', 'Count']
            
            color_map = {
                'Open': '#ef4444',
                'In Progress': '#f59e0b', 
                'Closed': '#10b981'
            }
            
            fig_status = px.pie(
                status_count,
                values='Count',
                names='Status',
                title="Tickets by Status",
                color='Status',
                color_discrete_map=color_map,
                hole=0.4
            )
            fig_status.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Priority Distribution
        if 'Priority' in df.columns and not df.empty:
            priority_count = df['Priority'].value_counts().reset_index()
            priority_count.columns = ['Priority', 'Count']
            
            priority_order = ['Low', 'Medium', 'High', 'Critical']
            priority_count['Priority'] = pd.Categorical(priority_count['Priority'], categories=priority_order, ordered=True)
            priority_count = priority_count.sort_values('Priority')
            
            color_map = {
                'Low': '#3b82f6',
                'Medium': '#f59e0b',
                'High': '#ef4444',
                'Critical': '#7f1d1d'
            }
            
            fig_priority = px.bar(
                priority_count,
                x='Priority',
                y='Count',
                color='Priority',
                title="Tickets by Priority",
                text='Count',
                color_discrete_map=color_map
            )
            fig_priority.update_traces(textposition='outside')
            fig_priority.update_layout(showlegend=False)
            st.plotly_chart(fig_priority, use_container_width=True)
    
    # All Tickets Table
    st.subheader("📊 All IT Tickets")
    st.dataframe(df, use_container_width=True)

# ----------------------------------------
# TAB 2: MANAGE TICKETS
# ----------------------------------------
with tab2:
    # Add Ticket
    with st.expander("➕ Add New Ticket", expanded=True):
        with st.form("add_ticket"):
            subject = st.text_input("Subject")
            issue = st.text_area("Issue")
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            status = st.selectbox("Status", ["Open", "In Progress", "Closed"])
            created_by = st.text_input("Created By")
            assigned_to = st.text_input("Assigned To")
            submitted = st.form_submit_button("Add Ticket")
            if submitted:
                new_row = pd.DataFrame({
                    "Subject": [subject],
                    "Issue": [issue],
                    "Priority": [priority],
                    "Status": [status],
                    "Created By": [created_by],
                    "Created On": [pd.Timestamp.now()],
                    "Resolved On": [""],
                    "Assigned To": [assigned_to]
                })
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(FILE_PATH, index=False)
                st.success("Ticket added successfully!")
                st.rerun()
    
    # Update Ticket
    with st.expander("✏️ Update Ticket"):
        if not df.empty:
            update_index = st.number_input("Row Number to Update", 0, len(df)-1, 0)
            if st.button("Load Ticket for Update"):
                row = df.iloc[update_index]
                with st.form("update_form"):
                    subject = st.text_input("Subject", row['Subject'])
                    issue = st.text_area("Issue", row['Issue'])
                    priority = st.selectbox(
                        "Priority",
                        ["Low", "Medium", "High", "Critical"],
                        index=["Low","Medium","High","Critical"].index(row['Priority']) if row['Priority'] in ["Low","Medium","High","Critical"] else 0
                    )
                    status = st.selectbox(
                        "Status",
                        ["Open","In Progress","Closed"],
                        index=["Open","In Progress","Closed"].index(row['Status']) if row['Status'] in ["Open","In Progress","Closed"] else 0
                    )
                    created_by = st.text_input("Created By", row['Created By'])
                    assigned_to = st.text_input("Assigned To", row.get('Assigned To', ''))
                    
                    if st.form_submit_button("Update Ticket"):
                        df.at[update_index, 'Subject'] = subject
                        df.at[update_index, 'Issue'] = issue
                        df.at[update_index, 'Priority'] = priority
                        df.at[update_index, 'Status'] = status
                        df.at[update_index, 'Created By'] = created_by
                        df.at[update_index, 'Assigned To'] = assigned_to
                        
                        # Auto-set resolved date if status is Closed
                        if status == "Closed" and pd.isna(df.at[update_index, 'Resolved On']):
                            df.at[update_index, 'Resolved On'] = pd.Timestamp.now()
                        
                        df.to_csv(FILE_PATH, index=False)
                        st.success("Ticket updated!")
                        st.rerun()
    
    # Delete Ticket
    with st.expander("🗑️ Delete Ticket"):
        if not df.empty:
            delete_index = st.number_input("Row Number to Delete", 0, len(df)-1, 0, key="del_index")
            if st.button("Delete Ticket"):
                df = df.drop(delete_index).reset_index(drop=True)
                df.to_csv(FILE_PATH, index=False)
                st.success("Ticket deleted!")
                st.rerun()
    
    # AI Assistant
    with st.expander("🤖 AI Assistant"):
        query = st.text_input("Ask about IT Tickets", key="ai_query")
        if st.button("Get Answer"):
            filtered = df[df.apply(lambda row: query.lower() in str(row).lower(), axis=1)]
            if not filtered.empty:
                st.dataframe(filtered, use_container_width=True)
            else:
                st.write("No matching tickets found.")