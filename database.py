import sqlite3
from pathlib import Path

import pandas as pd


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
                source TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
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


def add_expense(amount, date, category, description, reflection=""):
    if category not in CATEGORIES:
        raise ValueError("Expense category must be one of the Kakeibo categories.")

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO expenses (amount, date, category, description, reflection)
            VALUES (?, ?, ?, ?, ?)
            """,
            (float(amount), date.isoformat(), category, description.strip(), reflection.strip()),
        )


def get_expenses():
    with get_connection() as conn:
        expenses = pd.read_sql_query(
            """
            SELECT id, date, description, category, amount, reflection
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

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO incomes (amount, date, source, notes)
            VALUES (?, ?, ?, ?)
            """,
            (float(amount), date.isoformat(), source.strip(), notes.strip()),
        )


def get_incomes():
    with get_connection() as conn:
        incomes = pd.read_sql_query(
            """
            SELECT id, date, source, amount, notes
            FROM incomes
            ORDER BY date DESC, id DESC
            """,
            conn,
        )

    if not incomes.empty:
        incomes["date"] = pd.to_datetime(incomes["date"])
    return incomes
