import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt
import pandas as pd

IST = timezone(timedelta(hours=5, minutes=30))


DB_PATH = Path(__file__).with_name("kakeibo.db")
CATEGORIES = [
    "Survival (Needs)",
    "Optional (Wants)",
    "Culture (Growth & Learning)",
    "Extra (Unexpected)",
]
INCOME_SOURCES = [
    "Salary",
    "Bonus",
    "Rent Received",
    "Interest",
    "Other",
]
CATEGORY_ALIASES = {
    "Survival": "Survival (Needs)",
    "Optional": "Optional (Wants)",
    "Culture": "Culture (Growth & Learning)",
    "Extra": "Extra (Unexpected)",
}


def get_connection():
    return sqlite3.connect(DB_PATH)


def migrate_db():
    """
    Perform database migrations to transition from single-user to multi-user isolated data.
    Ensures that a default 'legacy' user is created and all pre-existing records are
    associated with this user so that no historical data is lost.
    """
    with get_connection() as conn:
        # Create users table if not exists
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Check if legacy user exists
        legacy_user = conn.execute("SELECT id FROM users WHERE username = 'legacy'").fetchone()
        if not legacy_user:
            legacy_hash = bcrypt.hashpw(b"legacy", bcrypt.gensalt()).decode("utf-8")
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ("legacy", legacy_hash),
            )
            legacy_user_id = 1
        else:
            legacy_user_id = legacy_user[0]

    # Perform table migrations for tables missing user_id
    tables_to_migrate = ["expenses", "incomes", "goals", "monthly_goals"]
    for table in tables_to_migrate:
        with get_connection() as conn:
            # Check if table exists
            table_exists = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table,),
            ).fetchone()
            if not table_exists:
                continue

            # Check if user_id column exists
            columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
            if "user_id" not in columns:
                if table == "expenses":
                    conn.execute("ALTER TABLE expenses RENAME TO old_expenses")
                    conn.execute(
                        """
                        CREATE TABLE expenses (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            amount REAL NOT NULL CHECK(amount > 0),
                            date TEXT NOT NULL,
                            time TEXT NOT NULL,
                            category TEXT NOT NULL,
                            description TEXT NOT NULL,
                            reflection TEXT DEFAULT '',
                            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                        )
                        """
                    )
                    conn.execute(
                        """
                        INSERT INTO expenses (id, user_id, amount, date, time, category, description, reflection, created_at)
                        SELECT id, ?, amount, date, time, category, description, reflection, created_at
                        FROM old_expenses
                        """,
                        (legacy_user_id,),
                    )
                    conn.execute("DROP TABLE old_expenses")

                elif table == "incomes":
                    conn.execute("ALTER TABLE incomes RENAME TO old_incomes")
                    conn.execute(
                        """
                        CREATE TABLE incomes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            amount REAL NOT NULL CHECK(amount > 0),
                            date TEXT NOT NULL,
                            time TEXT NOT NULL,
                            source TEXT NOT NULL,
                            notes TEXT DEFAULT '',
                            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                        )
                        """
                    )
                    conn.execute(
                        """
                        INSERT INTO incomes (id, user_id, amount, date, time, source, notes, created_at)
                        SELECT id, ?, amount, date, time, source, notes, created_at
                        FROM old_incomes
                        """,
                        (legacy_user_id,),
                    )
                    conn.execute("DROP TABLE old_incomes")

                elif table == "goals":
                    conn.execute("ALTER TABLE goals RENAME TO old_goals")
                    conn.execute(
                        """
                        CREATE TABLE goals (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL UNIQUE,
                            monthly_income REAL NOT NULL DEFAULT 0,
                            target_savings REAL NOT NULL DEFAULT 0,
                            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                        )
                        """
                    )
                    conn.execute(
                        """
                        INSERT INTO goals (user_id, monthly_income, target_savings, updated_at)
                        SELECT ?, monthly_income, target_savings, updated_at
                        FROM old_goals
                        """,
                        (legacy_user_id,),
                    )
                    conn.execute("DROP TABLE old_goals")

                elif table == "monthly_goals":
                    conn.execute("ALTER TABLE monthly_goals RENAME TO old_monthly_goals")
                    conn.execute(
                        """
                        CREATE TABLE monthly_goals (
                            user_id INTEGER NOT NULL,
                            month_key TEXT NOT NULL,
                            monthly_income REAL NOT NULL DEFAULT 0,
                            target_savings REAL NOT NULL DEFAULT 0,
                            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY (user_id, month_key),
                            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                        )
                        """
                    )
                    conn.execute(
                        """
                        INSERT INTO monthly_goals (user_id, month_key, monthly_income, target_savings, updated_at)
                        SELECT ?, month_key, monthly_income, target_savings, updated_at
                        FROM old_monthly_goals
                        """,
                        (legacy_user_id,),
                    )
                    conn.execute("DROP TABLE old_monthly_goals")


def init_db():
    # Run migrations first to handle existing databases
    migrate_db()

    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                reflection TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                source TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        for table, column_def in [
            ("expenses", "time TEXT NOT NULL DEFAULT ''"),
            ("incomes", "time TEXT NOT NULL DEFAULT ''"),
        ]:
            existing_columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
            if column_def.split()[0] not in existing_columns:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                monthly_income REAL NOT NULL DEFAULT 0,
                target_savings REAL NOT NULL DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS monthly_goals (
                user_id INTEGER NOT NULL,
                month_key TEXT NOT NULL,
                monthly_income REAL NOT NULL DEFAULT 0,
                target_savings REAL NOT NULL DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, month_key),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                usefulness_rating INTEGER,
                comments TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )


def save_goal(user_id, monthly_income, target_savings):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO goals (user_id, monthly_income, target_savings, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                monthly_income = excluded.monthly_income,
                target_savings = excluded.target_savings,
                updated_at = CURRENT_TIMESTAMP
            """,
            (int(user_id), float(monthly_income), float(target_savings)),
        )


def get_goal(user_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT monthly_income, target_savings FROM goals WHERE user_id = ?",
            (int(user_id),),
        ).fetchone()
    if row is None:
        return {"monthly_income": 0.0, "target_savings": 0.0}
    return {"monthly_income": row[0], "target_savings": row[1]}


def save_monthly_goal(user_id, month_key, monthly_income, target_savings):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO monthly_goals (user_id, month_key, monthly_income, target_savings, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, month_key) DO UPDATE SET
                monthly_income = excluded.monthly_income,
                target_savings = excluded.target_savings,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                int(user_id),
                month_key.strip(),
                float(monthly_income),
                float(target_savings),
            ),
        )


def get_monthly_goal(user_id, month_key):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT monthly_income, target_savings FROM monthly_goals WHERE user_id = ? AND month_key = ?",
            (int(user_id), month_key.strip()),
        ).fetchone()
    if row is None:
        return {"monthly_income": 0.0, "target_savings": 0.0}
    return {"monthly_income": row[0], "target_savings": row[1]}


def add_expense(user_id, amount, date, category, description, reflection=""):
    if category not in CATEGORIES:
        raise ValueError("Expense category must be one of the Kakeibo categories.")

    entry_time = datetime.now(IST).strftime("%H:%M:%S")
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO expenses (user_id, amount, date, time, category, description, reflection)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(user_id),
                float(amount),
                date.isoformat(),
                entry_time,
                category.strip(),
                description.strip(),
                reflection.strip(),
            ),
        )


def get_expenses(user_id):
    with get_connection() as conn:
        expenses = pd.read_sql_query(
            """
            SELECT id, date, time, description, category, amount, reflection
            FROM expenses
            WHERE user_id = ?
            ORDER BY date DESC, id DESC
            """,
            conn,
            params=(int(user_id),),
        )

    if not expenses.empty:
        expenses["date"] = pd.to_datetime(expenses["date"])
        expenses["category"] = expenses["category"].replace(CATEGORY_ALIASES)
    return expenses


def add_income(user_id, amount, date, source, notes=""):
    if float(amount) <= 0:
        raise ValueError("Income amount must be greater than zero.")

    entry_time = datetime.now(IST).strftime("%H:%M:%S")
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO incomes (user_id, amount, date, time, source, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                int(user_id),
                float(amount),
                date.isoformat(),
                entry_time,
                source.strip(),
                notes.strip(),
            ),
        )


def get_incomes(user_id):
    with get_connection() as conn:
        incomes = pd.read_sql_query(
            """
            SELECT id, date, time, source, amount, notes
            FROM incomes
            WHERE user_id = ?
            ORDER BY date DESC, id DESC
            """,
            conn,
            params=(int(user_id),),
        )

    if not incomes.empty:
        incomes["date"] = pd.to_datetime(incomes["date"])
    return incomes


def delete_income(user_id, income_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM incomes WHERE id = ? AND user_id = ?",
            (int(income_id), int(user_id)),
        )


def delete_expense(user_id, expense_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM expenses WHERE id = ? AND user_id = ?",
            (int(expense_id), int(user_id)),
        )


def save_feedback(user_id, rating, usefulness_rating, comments):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO feedback (user_id, rating, usefulness_rating, comments)
            VALUES (?, ?, ?, ?)
            """,
            (int(user_id), int(rating), int(usefulness_rating), comments.strip()),
        )


def get_all_feedback(limit=10):
    with get_connection() as conn:
        feedback_df = pd.read_sql_query(
            """
            SELECT f.rating, f.usefulness_rating, f.comments, f.created_at, u.username
            FROM feedback f
            JOIN users u ON f.user_id = u.id
            ORDER BY f.created_at DESC
            LIMIT ?
            """,
            conn,
            params=(int(limit),),
        )
    return feedback_df


def get_feedback_stats():
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*),
                AVG(rating),
                AVG(usefulness_rating),
                SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END)
            FROM feedback
            """
        ).fetchone()

    if not row or row[0] == 0:
        return {
            "total_reviews": 0,
            "avg_rating": 0.0,
            "avg_usefulness_rating": 0.0,
            "satisfaction_pct": 0.0,
        }

    total = row[0]
    avg_rating = row[1] or 0.0
    avg_usefulness = row[2] or 0.0
    high_ratings = row[3] or 0
    satisfaction_pct = (high_ratings / total) * 100.0

    return {
        "total_reviews": total,
        "avg_rating": avg_rating,
        "avg_usefulness_rating": avg_usefulness,
        "satisfaction_pct": satisfaction_pct,
    }


def get_supabase_client():
    """
    Initialize and return the Supabase client safely from Streamlit secrets.
    Returns None if secrets are missing or connection fails.
    """
    import streamlit as st

    if "SUPABASE_URL" not in st.secrets or "SUPABASE_ANON_KEY" not in st.secrets:
        return None
    try:
        from supabase import create_client

        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception:
        import traceback

        traceback.print_exc()
        return None


def save_feedback_supabase(user_id, username, rating, usefulness_rating, comments):
    """
    Save user feedback to Supabase table.
    """
    client = get_supabase_client()
    if not client:
        raise ConnectionError("Feedback service temporarily unavailable.")

    data = {
        "user_id": int(user_id),
        "username": username,
        "rating": int(rating),
        "ai_usefulness_rating": int(usefulness_rating),
        "comments": comments.strip(),
    }
    try:
        client.table("feedback").insert(data).execute()
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise e


def get_feedback_supabase():
    """
    Fetch all feedback entries from Supabase, sorted newest first.
    """
    client = get_supabase_client()
    if not client:
        return pd.DataFrame()

    try:
        response = client.table("feedback").select("*").order("created_at", desc=True).execute()
        data = response.data
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"])
        return df
    except Exception:
        import traceback

        traceback.print_exc()
        return pd.DataFrame()


def get_feedback_stats_supabase(df=None):
    """
    Compute feedback statistics from Supabase feedback data.
    """
    if df is None or df.empty:
        df = get_feedback_supabase()

    if df.empty:
        return {
            "total_reviews": 0,
            "avg_rating": 0.0,
            "avg_usefulness_rating": 0.0,
            "five_star_count": 0,
            "satisfaction_pct": 0.0,
        }

    total = len(df)
    avg_rating = float(df["rating"].mean())
    avg_usefulness = float(df["ai_usefulness_rating"].mean())
    five_star_count = int((df["rating"] == 5).sum())
    high_ratings = int((df["rating"] >= 4).sum())
    satisfaction_pct = (high_ratings / total) * 100.0

    return {
        "total_reviews": total,
        "avg_rating": avg_rating,
        "avg_usefulness_rating": avg_usefulness,
        "five_star_count": five_star_count,
        "satisfaction_pct": satisfaction_pct,
    }
