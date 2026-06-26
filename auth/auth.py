import logging
import sqlite3

import bcrypt
import streamlit as st

from database import get_connection, get_supabase_client

# Configure logging
logger = logging.getLogger("kakeibo_auth")
logger.setLevel(logging.INFO)
if not logger.handlers:
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(sh)


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


def create_user(username: str, password: str, email: str = "") -> tuple[bool, str]:
    """
    Create a new user. Returns (success_bool, message).
    """
    username = username.strip()
    email = email.strip()
    if not username:
        logger.warning("Registration failed: empty username.")
        return False, "Username cannot be empty."
    if len(password) < 6:
        logger.warning(f"Registration failed for user '{username}': password too short.")
        return False, "Password must be at least 6 characters long."

    hashed = hash_password(password)

    # Try to connect to Supabase
    client = get_supabase_client()
    if client:
        logger.info(f"Supabase detected. Attempting to register user '{username}' on Supabase.")
        try:
            # Check if username exists in Supabase
            res = client.table("users").select("id").eq("username", username).execute()
            if res.data:
                logger.warning(f"Registration failed: username '{username}' already taken in Supabase.")
                return False, f"Username '{username}' is already taken."

            # Insert user into Supabase
            user_data = {"username": username, "email": email or None, "password_hash": hashed}
            res_insert = client.table("users").insert(user_data).execute()
            if not res_insert.data:
                raise RuntimeError("Failed to insert user into Supabase.")

            supabase_user_id = res_insert.data[0]["id"]
            logger.info(f"User '{username}' registered in Supabase with ID {supabase_user_id}.")

            # Sync to local SQLite users table to satisfy foreign keys
            with get_connection() as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (?, ?, ?)",
                    (supabase_user_id, username, hashed),
                )
                logger.info(f"User '{username}' synced to local SQLite with ID {supabase_user_id}.")

            return True, "User registered successfully."
        except Exception as e:
            logger.error(f"Error creating user in Supabase: {str(e)}")
            return False, f"Error creating user: {str(e)}"
    else:
        # Fall back to local SQLite only
        logger.info(f"Supabase not configured. Registering user '{username}' locally in SQLite.")
        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, hashed),
                )
                local_id = cursor.lastrowid
                logger.info(f"User '{username}' registered in local SQLite with ID {local_id}.")
                return True, "User registered successfully."
        except sqlite3.IntegrityError:
            logger.warning(f"Registration failed: username '{username}' already taken in SQLite.")
            return False, f"Username '{username}' is already taken."
        except Exception as e:
            logger.error(f"Error creating user in SQLite: {str(e)}")
            return False, f"Error creating user: {str(e)}"


def authenticate_user(username: str, password: str) -> tuple[bool, str, int | None]:
    """
    Authenticate a user. Returns (success_bool, message, user_id).
    """
    username = username.strip()
    if not username or not password:
        logger.warning("Authentication failed: empty credentials.")
        return False, "Username and password cannot be empty.", None

    client = get_supabase_client()
    if client:
        logger.info(f"Supabase detected. Authenticating user '{username}' against Supabase.")
        try:
            res = client.table("users").select("id, password_hash").eq("username", username).execute()
            if not res.data:
                logger.warning(f"Authentication failed: user '{username}' not found in Supabase.")
                return False, "Invalid username or password.", None

            supabase_user_id = res.data[0]["id"]
            hashed = res.data[0]["password_hash"]

            if verify_password(password, hashed):
                logger.info(f"Authentication successful for user '{username}' (ID: {supabase_user_id}) on Supabase.")
                # Sync user details to local SQLite users table if missing (e.g. on container restart)
                with get_connection() as conn:
                    row = conn.execute("SELECT id FROM users WHERE id = ?", (supabase_user_id,)).fetchone()
                    if not row:
                        conn.execute(
                            "INSERT OR REPLACE INTO users (id, username, password_hash) VALUES (?, ?, ?)",
                            (supabase_user_id, username, hashed),
                        )
                        logger.info(f"User '{username}' (ID: {supabase_user_id}) dynamically restored in local SQLite.")
                return True, "Authenticated successfully.", supabase_user_id
            else:
                logger.warning(f"Authentication failed: invalid password for user '{username}'.")
                return False, "Invalid username or password.", None
        except Exception as e:
            logger.error(f"Authentication error via Supabase: {str(e)}")
            return False, f"Authentication error: {str(e)}", None
    else:
        # Fall back to local SQLite only
        logger.info(f"Supabase not configured. Authenticating user '{username}' against SQLite.")
        try:
            with get_connection() as conn:
                row = conn.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,)).fetchone()

            if not row:
                logger.warning(f"Authentication failed: user '{username}' not found in SQLite.")
                return False, "Invalid username or password.", None

            user_id, hashed = row
            if verify_password(password, hashed):
                logger.info(f"Authentication successful for user '{username}' (ID: {user_id}) on SQLite.")
                return True, "Authenticated successfully.", user_id
            else:
                logger.warning(f"Authentication failed: invalid password for user '{username}'.")
                return False, "Invalid username or password.", None
        except Exception as e:
            logger.error(f"Authentication error via SQLite: {str(e)}")
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
