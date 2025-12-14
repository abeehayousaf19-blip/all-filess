import streamlit as st

st.set_page_config(page_title="AI Assistant")

# Login protection
if "user" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

st.title("AI Assistant")
st.write("Ask questions about the platform features.")

# Chat history
if "chat" not in st.session_state:
    st.session_state["chat"] = []

user_input = st.text_input("Ask a question")

if st.button("Send"):
    if user_input.strip():
        st.session_state["chat"].append(("User", user_input))

        msg = user_input.lower()
        if "incident" in msg:
            reply = "Cybersecurity incidents can be viewed and added on the Cybersecurity page."
        elif "ticket" in msg:
            reply = "IT tickets are managed in the IT Operations page."
        elif "dataset" in msg:
            reply = "Datasets can be added and viewed in the Data Science page."
        elif "login" in msg:
            reply = "Users must log in before accessing platform features."
        else:
            reply = "I can help with incidents, tickets, datasets, or login."

        st.session_state["chat"].append(("Assistant", reply))
        st.rerun()

st.divider()

# Display conversation
for role, message in st.session_state["chat"]:
    st.write(f"**{role}:** {message}")
