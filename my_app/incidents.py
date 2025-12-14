import pandas as pd
import streamlit as st
from app.data.db import connect_database

# ---------------------------------------------------
# ROLE CHECKS
# ---------------------------------------------------
def require_admin():
    if st.session_state.get("role") != "admin":
        raise PermissionError("Only admin may delete incidents.")

def require_admin_or_analyst():
    if st.session_state.get("role") not in ("admin", "analyst"):
        raise PermissionError("Only admin/analyst may create or update incidents.")


# ---------------------------------------------------
# INSERT INCIDENT (Admin + Analyst)
# ---------------------------------------------------
def insert_incident(conn, incident_id, timestamp, incidents_type, severity, category, status, description):
    require_admin_or_analyst()

    cursor = conn.cursor()
    query = """
        INSERT INTO cyber_incidents
        (incident_id, timestamp, incidents_type, severity, category, status, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (incident_id, timestamp, incidents_type, severity, category, status, description))
    conn.commit()
    return cursor.lastrowid


# ---------------------------------------------------
# GET ALL INCIDENTS (Everyone)
# ---------------------------------------------------
def get_all_incidents(conn):
    query = """
        SELECT *
        FROM cyber_incidents
        ORDER BY timestamp DESC
    """
    return pd.read_sql_query(query, conn)



def get_incidents_by_severity(conn, severity):
    return pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE severity = ? ORDER BY id DESC",
        conn,
        params=(severity,)
    )


def get_incidents_by_status(conn, status):
    return pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE status = ? ORDER BY id DESC",
        conn,
        params=(status,)
    )


# ---------------------------------------------------
# UPDATE (Admin + Analyst)
# ---------------------------------------------------
def update_incident_status(conn, incident_id, new_status):
    require_admin_or_analyst()
    cursor = conn.cursor()
    cursor.execute("UPDATE cyber_incidents SET status = ? WHERE incident_id = ?", (new_status, incident_id))
    conn.commit()
    return cursor.rowcount > 0


# ---------------------------------------------------
# DELETE (Admin only)
# ---------------------------------------------------
def delete_incident(conn, incident_id):
    require_admin()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cyber_incidents WHERE incident_id = ?", (incident_id,))
    conn.commit()
    return cursor.rowcount > 0


# ---------------------------------------------------
# ANALYTICAL QUERIES
# ---------------------------------------------------
def get_incidents_by_type_count(conn):
    return pd.read_sql_query("""
        SELECT incidents_type, COUNT(*) AS count
        FROM cyber_incidents
        GROUP BY incidents_type
        ORDER BY count DESC
    """, conn)


def get_high_severity_by_status(conn):
    return pd.read_sql_query("""
        SELECT status, COUNT(*) AS count
        FROM cyber_incidents
        WHERE severity = 'High'
        GROUP BY status
        ORDER BY count DESC
    """, conn)


def get_incident_types_with_many_cases(conn, min_count=5):
    return pd.read_sql_query("""
        SELECT incidents_type, COUNT(*) AS count
        FROM cyber_incidents
        GROUP BY incidents_type
        HAVING COUNT(*) > ?
        ORDER BY count DESC
    """, conn, params=(min_count,))




import pandas as pd
from app.data.db import connect_database

# ---------------------------------------------------------
# INSERT INCIDENT
# ---------------------------------------------------------

def insert_incident(conn, incident_id, timestamp, incidents_type, severity, category, status, description):
    """
    Insert a new cyber incident into the database.

    Args:
        conn: Database connection
        incident_id: Incident identifier (string or number)
        timestamp: Timestamp string (YYYY-MM-DD HH:MM:SS)
        incidents_type: Type of incident (e.g., 'Phishing', 'Malware')
        severity: Severity level (High, Medium, Low)
        category: Category of the incident
        status: Current status (Open, Closed, etc.)
        description: Detailed description

    Returns:
        int: ID of the newly inserted incident
    """
    cursor = conn.cursor()

    query = """
        INSERT INTO cyber_incidents
        (incident_id, timestamp, incidents_type, severity, category, status, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(query, (
        incident_id,
        timestamp,
        incidents_type,
        severity,
        category,
        status,
        description
    ))

    conn.commit()
    return cursor.lastrowid


# ---------------------------------------------------------
# GET ALL INCIDENTS
# ---------------------------------------------------------

def get_all_incidents(conn):
    query = """
        SELECT *
        FROM cyber_incidents
        ORDER BY timestamp DESC
    """
    return pd.read_sql_query(query, conn)


# ---------------------------------------------------------
# GET INCIDENTS BY SEVERITY
# ---------------------------------------------------------

def get_incidents_by_severity(conn, severity):
    query = """
        SELECT *
        FROM cyber_incidents
        WHERE severity = ?
        ORDER BY id DESC
    """
    df = pd.read_sql_query(query, conn, params=(severity,))
    return df


# ---------------------------------------------------------
# GET INCIDENTS BY STATUS
# ---------------------------------------------------------

def get_incidents_by_status(conn, status):
    """
    Retrieve incidents filtered by status.
    """
    query = """
        SELECT *
        FROM cyber_incidents
        WHERE status = ?
        ORDER BY id DESC
    """
    df = pd.read_sql_query(query, conn, params=(status,))
    return df
#--------------------------------------------------------------
# UPDATING INCIDENT STATUS
#--------------------------------------------------------------

def update_incident_status(conn, incident_id, new_status):
    """
    Update the status of an incident by its incident_id.
    """
    cursor = conn.cursor()

    query = """
        UPDATE cyber_incidents
        SET status = ?
        WHERE incident_id = ?
    """

    cursor.execute(query, (new_status, incident_id))
    conn.commit()

    if cursor.rowcount > 0:
        print(f"✅ Incident {incident_id} status updated to '{new_status}'.")
        return True
    else:
        print(f"⚠️ No incident found with incident_id {incident_id}.")
        return False

def delete_incident(conn, incident_id):
    cursor = conn.cursor()

    query = """
        DELETE FROM cyber_incidents
        WHERE incident_id = ?
    """

    cursor.execute(query, (incident_id,))
    conn.commit()

    if cursor.rowcount > 0:
        print(f"🗑️ Incident {incident_id} deleted successfully.")
        return True
    else:
        print(f"⚠️ No incident found with incident_id {incident_id}.")
        return False

# ---------------------------------------------------------
# 1. Count incidents by type
# ---------------------------------------------------------
def get_incidents_by_type_count(conn):
    query = """
    SELECT incidents_type, COUNT(*) AS count
    FROM cyber_incidents
    GROUP BY incidents_type
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df


# ---------------------------------------------------------
# 2. Count high-severity incidents grouped by status
# ---------------------------------------------------------
def get_high_severity_by_status(conn):
    query = """
    SELECT status, COUNT(*) AS count
    FROM cyber_incidents
    WHERE severity = 'High'
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df


# ---------------------------------------------------------
# 3. Find incident types with more than min_count occurrences
# ---------------------------------------------------------
def get_incident_types_with_many_cases(conn, min_count=5):
    query = """
    SELECT incidents_type, COUNT(*) AS count
    FROM cyber_incidents
    GROUP BY incidents_type
    HAVING COUNT(*) > ?
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn, params=(min_count,))
    return df
