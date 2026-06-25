import sqlite3

import bcrypt
import streamlit as st

from database import get_connection


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against a hash.
    """
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_user(username: str, password: str) -> tuple[bool, str]:
    """
    Create a new user. Returns (success_bool, message).
    """
    username = username.strip()
    if not username:
        return False, "Username cannot be empty."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    hashed = hash_password(password)
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed),
            )
            return True, "User registered successfully."
    except sqlite3.IntegrityError:
        return False, f"Username '{username}' is already taken."
    except Exception as e:
        return False, f"Error creating user: {str(e)}"


def authenticate_user(username: str, password: str) -> tuple[bool, str, int | None]:
    """
    Authenticate a user. Returns (success_bool, message, user_id).
    """
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty.", None

    try:
        with get_connection() as conn:
            row = conn.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)).fetchone()

        if not row:
            return False, "Invalid username or password.", None

        user_id, hashed = row
        if verify_password(password, hashed):
            return True, "Authenticated successfully.", user_id
        else:
            return False, "Invalid username or password.", None
    except Exception as e:
        return False, f"Authentication error: {str(e)}", None


def logout_user():
    """
    Logout the current user and clear session state.
    """
    st.session_state["authenticated"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    st.session_state["chat_messages"] = []


def get_current_user() -> tuple[str | None, int | None]:
    """
    Get current logged in user.
    """
    if st.session_state.get("authenticated"):
        return st.session_state.get("username"), st.session_state.get("user_id")
    return None, None
