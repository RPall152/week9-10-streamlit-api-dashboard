import pandas as pd
from pathlib import Path
from app.data.db import connect_database, DATA_DIR


def load_csv_to_table(conn, csv_path, table_name):
    print(f"DEBUG: Looking for {csv_path}")

    path = Path(csv_path)

    # Check if file exists
    if not path.exists():
        print(f"⚠️  Warning: {csv_path} not found. Skipping.")
        return 0

    # Read CSV
    df = pd.read_csv(path)
    print(f"DEBUG: Loaded {len(df)} rows for {table_name}")


    # Clean column names
    df.columns = df.columns.str.strip()

    # Preview
    print(f"\n📄 Loading {csv_path}...")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Rows: {len(df)}")

    # Insert into database
    df.to_sql(table_name, conn, if_exists='append', index=False)

    print(f"   ✔ Loaded {len(df)} rows into '{table_name}' table.")
    return len(df)


def load_all_csv_data(conn):
    print("\n🔄 Loading CSV data...")

    total = 0

    total += load_csv_to_table(
        conn,
        DATA_DIR / "cyber_incidents.csv",
        "cyber_incidents"
    )

    total += load_csv_to_table(
        conn,
        DATA_DIR / "datasets_metadata.csv",
        "datasets_metadata"
    )

    total += load_csv_to_table(
        conn,
        DATA_DIR / "it_tickets.csv",
        "it_tickets"
    )

    print(f"\n✅ Total rows loaded: {total}")
    return total



if __name__ == "__main__":
    from app.data.db import connect_database

    conn = connect_database()
    load_all_csv_data(conn)


cursor = conn.cursor()

for t in ["cyber_incidents", "datasets_metadata", "it_tickets"]:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    print(t, cursor.fetchone()[0])

conn.close()
