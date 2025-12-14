import bcrypt
from pathlib import Path
from app.data.users import get_user_by_username, insert_user 


# ---------------------------------------------------------
# REGISTER USER
# ---------------------------------------------------------
def register_user(username, password, role="user"):
    # Validate input
    if not username or not password:
        return False, "Username and password are required."

    # Check if username already exists
    if get_user_by_username(username):
        return False, f"Username '{username}' already exists."

    # Hash the password
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"), 
        bcrypt.gensalt()
    ).decode("utf-8")

    # Insert user using your CRUD layer
    success = insert_user(username, password_hash, role)

    if not success:
        return False, "Error inserting user into database."

    return True, f"User '{username}' registered successfully with role '{role}'."


# ---------------------------------------------------------
# LOGIN USER
# ---------------------------------------------------------

def login_user(username, password):
    # Look up user (tuple: id, username, password_hash, role)
    user = get_user_by_username(username)

    if not user:
        return False, "User not found."

    user_id, uname, stored_hash, role = user

    # Verify password
    if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        return True, f"Login successful! Welcome {username} (role: {role})."

    return False, "Incorrect password."


# ---------------------------------------------------------
# MIGRATE USERS FROM users.txt
# ---------------------------------------------------------
import sqlite3
from pathlib import Path
from app.data.db import connect_database, DATA_DIR


def migrate_users_from_file(conn, filepath=DATA_DIR / "users.txt"):
    path = Path(filepath)

    # Check if file exists
    if not path.exists():
        print(f"Warning: {filepath} not found. Skipping migration.")
        return 0

    cursor = conn.cursor()
    migrated_count = 0

    # Read users.txt line by line
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Skip empty or commented lines
            if not line or line.startswith("#"):
                continue

            # Parse "username,password_hash,role"
            parts = [p.strip() for p in line.split(",")]

            if len(parts) < 2:
                print(f"Skipping invalid line: {line}")
                continue

            username = parts[0]
            password_hash = parts[1]
            role = parts[2] if len(parts) >= 3 else "user"

            # Insert user safely
            try:
                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, role)
                    VALUES (?, ?, ?)
                    """,
                    (username, password_hash, role)
                )
                migrated_count += 1

            except sqlite3.IntegrityError:
                # UNIQUE(username) constraint triggered
                print(f" User '{username}' already exists. Skipping.")

    conn.commit()
    return migrated_count


# ----------------------------------------------------------
# TEST MIGRATION (ONLY RUNS IF YOU RUN THIS FILE DIRECTLY)
# ----------------------------------------------------------
''''
if __name__ == "__main__":
    conn = connect_database()
    from schema import create_users_table  # local import

    create_users_table(conn)
    count = migrate_users_from_file(conn)

    print(f"\nSuccessfully migrated {count} user(s) from users.txt to database!")
    conn.close()
'''