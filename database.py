import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

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


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL CHECK(amount > 0),
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                reflection TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL CHECK(amount > 0),
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                source TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        for table, column_def in [
            ("expenses", "time TEXT NOT NULL DEFAULT ''"),
            ("incomes", "time TEXT NOT NULL DEFAULT ''"),
        ]:
            existing_columns = [
                row[1] for row in conn.execute(f"PRAGMA table_info({table})")
            ]
            if column_def.split()[0] not in existing_columns:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                monthly_income REAL NOT NULL DEFAULT 0,
                target_savings REAL NOT NULL DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO goals (id, monthly_income, target_savings)
            VALUES (1, 0, 0)
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS monthly_goals (
                month_key TEXT PRIMARY KEY,
                monthly_income REAL NOT NULL DEFAULT 0,
                target_savings REAL NOT NULL DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_goal(monthly_income, target_savings):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE goals
            SET monthly_income = ?, target_savings = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
            """,
            (float(monthly_income), float(target_savings)),
        )


def get_goal():
    with get_connection() as conn:
        row = conn.execute(
            "SELECT monthly_income, target_savings FROM goals WHERE id = 1"
        ).fetchone()
    return {"monthly_income": row[0], "target_savings": row[1]}


def save_monthly_goal(month_key, monthly_income, target_savings):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO monthly_goals (month_key, monthly_income, target_savings, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(month_key) DO UPDATE SET
                monthly_income = excluded.monthly_income,
                target_savings = excluded.target_savings,
                updated_at = CURRENT_TIMESTAMP
            """,
            (month_key.strip(), float(monthly_income), float(target_savings)),
        )


def get_monthly_goal(month_key):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT monthly_income, target_savings FROM monthly_goals WHERE month_key = ?",
            (month_key.strip(),),
        ).fetchone()
    if row is None:
        return {"monthly_income": 0.0, "target_savings": 0.0}
    return {"monthly_income": row[0], "target_savings": row[1]}


def add_expense(amount, date, category, description, reflection=""):
    if category not in CATEGORIES:
        raise ValueError("Expense category must be one of the Kakeibo categories.")

    entry_time = datetime.now(IST).strftime("%H:%M:%S")
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO expenses (amount, date, time, category, description, reflection)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                float(amount),
                date.isoformat(),
                entry_time,
                category.strip(),
                description.strip(),
                reflection.strip(),
            ),
        )


def get_expenses():
    with get_connection() as conn:
        expenses = pd.read_sql_query(
            """
            SELECT id, date, time, description, category, amount, reflection
            FROM expenses
            ORDER BY date DESC, id DESC
            """,
            conn,
        )

    if not expenses.empty:
        expenses["date"] = pd.to_datetime(expenses["date"])
        expenses["category"] = expenses["category"].replace(CATEGORY_ALIASES)
    return expenses


def add_income(amount, date, source, notes=""):
    if float(amount) <= 0:
        raise ValueError("Income amount must be greater than zero.")

    entry_time = datetime.now(IST).strftime("%H:%M:%S")
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO incomes (amount, date, time, source, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                float(amount),
                date.isoformat(),
                entry_time,
                source.strip(),
                notes.strip(),
            ),
        )


def get_incomes():
    with get_connection() as conn:
        incomes = pd.read_sql_query(
            """
            SELECT id, date, time, source, amount, notes
            FROM incomes
            ORDER BY date DESC, id DESC
            """,
            conn,
        )

    if not incomes.empty:
        incomes["date"] = pd.to_datetime(incomes["date"])
    return incomes


def delete_income(income_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM incomes WHERE id = ?", (int(income_id),))


def delete_expense(expense_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?", (int(expense_id),))
