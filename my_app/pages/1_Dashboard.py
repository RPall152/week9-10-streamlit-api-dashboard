from path_setup import *

import streamlit as st

from my_app.auth import (
    require_login,
    is_admin,
    is_analyst,
    is_user,
    can_create_or_update,
    can_delete
)

# -----------------------------
# AUTHENTICATION CHECK
# -----------------------------
require_login()
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to access the dashboard.")
    st.switch_page("Home.py")
    st.stop()

# -----------------------------
# PAGE TITLE
# -----------------------------
st.title("📊 Intelligence Platform Dashboard")

st.write(f"Welcome **{st.session_state.username}**! 👋")
st.write(f"Your role: **{st.session_state.role}**")

st.markdown("---")


# -----------------------------
# NAVIGATION BUTTONS
# -----------------------------
st.subheader("Navigate to a Domain")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📂 Cyber Incidents"):
        st.switch_page("pages/2_Incidents.py")

with col2:
    if st.button("📊 Datasets"):
        st.switch_page("pages/3_Datasets.py")

with col3:
    if st.button("🛠️ Tickets"):
        st.switch_page("pages/4_Tickets.py")


# -----------------------------
# LOGOUT BUTTON
# -----------------------------
st.markdown("---")

if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.success("You have been logged out.")
    st.switch_page("Home.py")
