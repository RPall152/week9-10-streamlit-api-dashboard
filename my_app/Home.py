from path_setup import *

import streamlit as st
from app.services.user_service import login_user, register_user
from app.data.db import connect_database

# SESSION INITIALIZATION

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "role" not in st.session_state:
    st.session_state.role = None


# If already logged in
if st.session_state.logged_in:
    st.switch_page("pages/1_Dashboard.py")


st.title("🔐 Intelligence Platform Login")
st.write("Welcome! Please log in or register below.")


st.subheader("Login")

login_username = st.text_input("Username", key="login_user")
login_password = st.text_input("Password", type="password", key="login_pass")

if st.button("Login"):
    success, msg = login_user(login_username, login_password)
    if success:
        st.success("Login successful!")

        # Save session data
        st.session_state.logged_in = True
        st.session_state.username = login_username

        # Get role from database
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ?", (login_username,))
        row = cursor.fetchone()
        conn.close()

        st.session_state.role = row[0] if row else "user"

        st.switch_page("pages/1_Dashboard.py")
    else:
        st.error(msg)


st.subheader("Register New Account")

reg_username = st.text_input("New Username", key="reg_user")
reg_password = st.text_input("New Password", type="password", key="reg_pass")
reg_role = st.selectbox("Role", ["user", "analyst", "admin"])

if st.button("Register"):
    success, msg = register_user(reg_username, reg_password, reg_role)
    if success:
        st.success(msg)
        st.info("You can now login using your credentials.")
    else:
        st.error(msg)



st.markdown("---")
st.caption("Week 9 – Streamlit Web Application • Intelligence Platform")
