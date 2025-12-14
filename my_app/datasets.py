import pandas as pd
from app.data.db import connect_database

def insert_dataset(conn, dataset_id, name, rows, columns, uploaded_by, upload_date):
    cursor = conn.cursor()
    query = """
        INSERT INTO datasets_metadata 
        (dataset_id, name, rows, columns, uploaded_by, upload_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (dataset_id, name, rows, columns, uploaded_by, upload_date))
    conn.commit()
    return cursor.lastrowid


def get_all_datasets(conn):
    query = "SELECT * FROM datasets_metadata ORDER BY upload_date DESC"
    return pd.read_sql_query(query, conn)


def delete_dataset(conn, dataset_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datasets_metadata WHERE dataset_id = ?", (dataset_id,))
    conn.commit()
    return cursor.rowcount > 0


def get_datasets_by_uploader(conn):
    query = """
        SELECT uploaded_by, COUNT(*) AS count
        FROM datasets_metadata
        GROUP BY uploaded_by
        ORDER BY count DESC
    """
    return pd.read_sql_query(query, conn)


def get_dataset_size_stats(conn):
    query = """
        SELECT name, rows, columns
        FROM datasets_metadata
    """
    return pd.read_sql_query(query, conn)
