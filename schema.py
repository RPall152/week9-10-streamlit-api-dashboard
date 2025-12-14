from app.data.db import connect_database

# ---------------------------------------------------------
# USERS TABLE
# ---------------------------------------------------------
def create_users_table(conn):

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    );
    """

    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    print("Users table created successfully!")

#------------------------------------------
# CYBER INCIDENTS TABLE
#------------------------------------------
def create_cyber_incidents_table(conn):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS cyber_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id TEXT,
        timestamp TEXT,
        incidents_type TEXT,
        severity TEXT,
        category TEXT,
        status TEXT,
        description TEXT
    );
    """

    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    print("Cyber incidents table recreated!")

#---------------------------------------------
# DATASETS TABLE
#----------------------------------------------
def create_datasets_metadata_table(conn):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS datasets_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id TEXT,
        name TEXT,
        rows INTEGER,
        columns INTEGER,
        uploaded_by TEXT,
        upload_date TEXT
    );
    """

    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    print("Datasets metadata table recreated!")

#-------------------------------------
# IT TICKETS TABLE
#-------------------------------------
def create_it_tickets_table(conn):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS it_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT,
        priority TEXT,
        description TEXT,
        status TEXT,
        assigned_to TEXT,
        created_at TEXT,
        resolution_time_hours INTEGER
    );
    """
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    print("IT tickets table recreated!")


def create_all_tables(conn):

    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)
    print("\nAll tables created successfully!")

'''
# Test run
if __name__ == "__main__":
    conn = connect_database()
    create_all_tables(conn)
    conn.close()
'''
