from app.data.db import connect_database

# ---------------------------------------------------------
# GET USER BY USERNAME
# ---------------------------------------------------------
def get_user_by_username(username: str):
    """Retrieve a user row by username."""
    conn = connect_database()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        return cursor.fetchone()

    finally:
        conn.close()


# ---------------------------------------------------------
# INSERT NEW USER
# ---------------------------------------------------------
def insert_user(username: str, password_hash: str, role: str = "user"):
    """Insert a new user safely."""
    conn = connect_database()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, role)
        )
        conn.commit()
        return True

    except Exception as e:
        print(f"Error inserting user: {e}")
        return False

    finally:
        conn.close()


# ---------------------------------------------------------
# DELETE USER
# ---------------------------------------------------------
def delete_user(username: str):
    """Delete a user by username."""
    conn = connect_database()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM users WHERE username = ?",
            (username,)
        )
        conn.commit()
        return cursor.rowcount > 0  # True if deleted

    finally:
        conn.close()


# ---------------------------------------------------------
# UPDATE USER ROLE
# ---------------------------------------------------------
def update_user_role(username: str, new_role: str):
    """Update the role of a user."""
    conn = connect_database()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE users SET role = ? WHERE username = ?",
            (new_role, username)
        )
        conn.commit()
        return cursor.rowcount > 0

    finally:
        conn.close()


# ---------------------------------------------------------
# UPDATE USER PASSWORD
# ---------------------------------------------------------
def update_user_password(username: str, new_password_hash: str):
    """Update a user's password hash."""
    conn = connect_database()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (new_password_hash, username)
        )
        conn.commit()
        return cursor.rowcount > 0

    finally:
        conn.close()