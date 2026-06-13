from datetime import date

import pytest

import database
from database import (
    add_expense,
    add_income,
    delete_expense,
    delete_income,
    get_all_feedback,
    get_expenses,
    get_feedback_stats,
    get_feedback_stats_supabase,
    get_feedback_supabase,
    get_goal,
    get_incomes,
    get_monthly_goal,
    save_feedback,
    save_feedback_supabase,
    save_goal,
    save_monthly_goal,
)


class MockTable:

    def __init__(self):
        self.data = []

    def insert(self, data):
        self.data.append(data)
        return self

    def select(self, *args):
        return self

    def order(self, *args, **kwargs):
        return self

    def execute(self):
        class Response:

            def __init__(self, data):
                self.data = data

        return Response(self.data)


class MockSupabase:

    def __init__(self):
        self._table = MockTable()

    def table(self, name):
        return self._table


@pytest.fixture
def mock_supabase_client(monkeypatch):
    mock_client = MockSupabase()
    # Pre-populate some dummy feedback
    mock_client.table("feedback").data = [
        {
            "user_id": 1,
            "username": "alice",
            "rating": 5,
            "ai_usefulness_rating": 4,
            "comments": "great",
            "created_at": "2026-06-12T12:00:00Z",
        },
        {
            "user_id": 2,
            "username": "bob",
            "rating": 4,
            "ai_usefulness_rating": 3,
            "comments": "ok",
            "created_at": "2026-06-12T13:00:00Z",
        },
    ]
    monkeypatch.setattr("database.get_supabase_client", lambda: mock_client)
    return mock_client


def test_goals():
    save_goal(1, 50000.0, 10000.0)
    goal = get_goal(1)
    assert goal["monthly_income"] == 50000.0
    assert goal["target_savings"] == 10000.0


def test_monthly_goals():
    # Save a composite monthly goal
    save_monthly_goal(1, "2026-06", 60000.0, 15000.0)
    goal = get_monthly_goal(1, "2026-06")
    assert goal["monthly_income"] == 60000.0
    assert goal["target_savings"] == 15000.0

    # Retrieve non-existent goal
    empty_goal = get_monthly_goal(1, "2099-12")
    assert empty_goal["monthly_income"] == 0.0
    assert empty_goal["target_savings"] == 0.0


def test_expenses():
    add_expense(
        user_id=1,
        amount=250.0,
        date=date(2026, 6, 12),
        category="Survival (Needs)",
        description="Groceries",
    )
    df = get_expenses(1)
    assert len(df) == 1
    assert df.iloc[0]["amount"] == 250.0
    assert df.iloc[0]["description"] == "Groceries"

    # Test delete expense
    expense_id = df.iloc[0]["id"]
    delete_expense(1, expense_id)
    df_after = get_expenses(1)
    assert len(df_after) == 0


def test_incomes():
    add_income(user_id=1, amount=1000.0, date=date(2026, 6, 12), source="Salary")
    df = get_incomes(1)
    assert len(df) == 1
    assert df.iloc[0]["amount"] == 1000.0

    # Test delete income
    income_id = df.iloc[0]["id"]
    delete_income(1, income_id)
    df_after = get_incomes(1)
    assert len(df_after) == 0


def test_sqlite_feedback():
    # Seed users for foreign key constraint in SQLite feedback table
    with database.get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (?, ?, ?)",
            (1, "tester", "dummyhash"),
        )

    # Save and retrieve feedback
    save_feedback(1, 5, 4, "loved the app!")
    df = get_all_feedback(limit=5)
    assert len(df) == 1
    assert df.iloc[0]["rating"] == 5
    assert df.iloc[0]["comments"] == "loved the app!"

    # Stats
    stats = get_feedback_stats()
    assert stats["total_reviews"] == 1
    assert stats["avg_rating"] == 5.0
    assert stats["satisfaction_pct"] == 100.0


def test_supabase_feedback(mock_supabase_client):
    # Retrieve mock entries
    df = get_feedback_supabase()
    assert len(df) == 2
    assert df.iloc[0]["username"] == "alice"

    # Stats calculation
    stats = get_feedback_stats_supabase(df)
    assert stats["total_reviews"] == 2
    assert stats["avg_rating"] == 4.5
    assert stats["five_star_count"] == 1
    assert stats["satisfaction_pct"] == 100.0

    # Insert entry
    save_feedback_supabase(3, "charlie", 3, 2, "neutral feedback")
    assert len(mock_supabase_client.table("feedback").data) == 3
    assert mock_supabase_client.table("feedback").data[-1]["username"] == "charlie"
