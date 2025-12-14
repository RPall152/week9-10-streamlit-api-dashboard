import pandas as pd
import streamlit as st


# ---------------------------------------------------
# ROLE CHECKS (Backend safety)
# ---------------------------------------------------
def require_admin():
    if st.session_state.get("role") != "admin":
        raise PermissionError("Only admin users may delete tickets.")


def require_admin_or_analyst():
    if st.session_state.get("role") not in ("admin", "analyst"):
        raise PermissionError("Only admin or analyst users may create or update tickets.")


# ---------------------------------------------------
# CREATE TICKET (Admin + Analyst)
# ---------------------------------------------------
def insert_ticket(
    conn,
    ticket_id,
    priority,
    description,
    status,
    assigned_to,
    created_at,
    resolution_time_hours
):
    require_admin_or_analyst()

    cursor = conn.cursor()
    query = """
        INSERT INTO it_tickets
        (ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(
        query,
        (
            ticket_id,
            priority,
            description,
            status,
            assigned_to,
            created_at,
            resolution_time_hours
        )
    )
    conn.commit()
    return cursor.lastrowid


# ---------------------------------------------------
# READ (Everyone)
# ---------------------------------------------------
def get_all_tickets(conn):
    query = "SELECT * FROM it_tickets ORDER BY created_at DESC"
    return pd.read_sql_query(query, conn)


# ---------------------------------------------------
# UPDATE (Admin + Analyst)
# ---------------------------------------------------
def update_ticket_status(conn, ticket_id, new_status):
    require_admin_or_analyst()

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE it_tickets SET status = ? WHERE ticket_id = ?",
        (new_status, ticket_id)
    )
    conn.commit()
    return cursor.rowcount > 0


# ---------------------------------------------------
# DELETE (Admin only)
# ---------------------------------------------------
def delete_ticket(conn, ticket_id):
    require_admin()

    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM it_tickets WHERE ticket_id = ?",
        (ticket_id,)
    )
    conn.commit()
    return cursor.rowcount > 0


# ===================================================
# 📊 ANALYTICS FUNCTIONS (USED BY STREAMLIT)
# ===================================================

# 1️⃣ Tickets by Priority
def get_tickets_by_priority(conn):
    query = """
        SELECT priority, COUNT(*) AS count
        FROM it_tickets
        GROUP BY priority
        ORDER BY count DESC
    """
    return pd.read_sql_query(query, conn)


# 2️⃣ Tickets by Status
def get_tickets_by_status(conn):
    query = """
        SELECT status, COUNT(*) AS count
        FROM it_tickets
        GROUP BY status
        ORDER BY count DESC
    """
    return pd.read_sql_query(query, conn)


# 3️⃣ Average Resolution Time by Priority
def get_avg_resolution_time(conn):
    query = """
        SELECT
            priority,
            ROUND(AVG(resolution_time_hours), 2) AS avg_resolution_hours
        FROM it_tickets
        WHERE resolution_time_hours IS NOT NULL
        GROUP BY priority
        ORDER BY avg_resolution_hours DESC
    """
    return pd.read_sql_query(query, conn)


# 4️⃣ Tickets Assigned Per User
def get_tickets_assigned_count(conn):
    query = """
        SELECT assigned_to, COUNT(*) AS count
        FROM it_tickets
        WHERE assigned_to IS NOT NULL AND assigned_to != ''
        GROUP BY assigned_to
        ORDER BY count DESC
    """
    return pd.read_sql_query(query, conn)
