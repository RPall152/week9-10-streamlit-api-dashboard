import sqlite3
from pathlib import Path

# Path to the DATA directory and database
DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"

# Ensure the DATA directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)


def connect_database(db_path=DB_PATH):
    """
    Connect to the SQLite database.
    Creates the database file if it doesn't exist.
    
    Args:
        db_path (Path): Path to the database file.
        
    Returns:
        sqlite3.Connection: Database connection object.
    """
    return sqlite3.connect(str(db_path))


# -----------------------------------------------------
# Optional: Self-test when run directly
# -----------------------------------------------------
if __name__ == "__main__":
    print("Testing database connection...")

    conn = connect_database()
    
    print("✔ Database connection successful!")
    print(f"Database type: {type(conn)}")
    
    conn.close()
    print("✔ Connection closed.")