import streamlit as st

# -----------------------------------------
# LOGIN CHECK
# -----------------------------------------
def require_login():
    """Require the user to be logged in before accessing a page."""
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.error("You must be logged in to access this page.")
        st.switch_page("Home.py")
        st.stop()

# -----------------------------------------
# ROLE HELPERS
# -----------------------------------------
def is_admin():
    return st.session_state.get("role") == "admin"

def is_analyst():
    return st.session_state.get("role") == "analyst"

def is_user():
    return st.session_state.get("role") == "user"

# -----------------------------------------
# PERMISSION HELPERS
# -----------------------------------------
def can_create_or_update():
    """Admins + Analysts can create + update."""
    return is_admin() or is_analyst()

def can_delete():
    """Only Admins may delete records."""
    return is_admin()
