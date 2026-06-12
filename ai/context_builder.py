import pandas as pd
from database import get_monthly_goal, get_expenses, get_incomes


def build_financial_context(selected_date: pd.Timestamp) -> str:
    """
    Query the database to generate a comprehensive, structured financial summary
    for the selected month to serve as context for the AI.
    """
    month_key = selected_date.strftime("%Y-%m")
    goal = get_monthly_goal(month_key)

    # Fetch transactions
    expenses_df = get_expenses()
    incomes_df = get_incomes()

    # Filter transactions to selected month
    def filter_to_month(df, date_col="date"):
        if df.empty:
            return df
        return df[
            (df[date_col].dt.month == selected_date.month)
            & (df[date_col].dt.year == selected_date.year)
        ]

    month_expenses = filter_to_month(expenses_df)
    month_incomes = filter_to_month(incomes_df)

    # Calculation of incomes
    fixed_income = float(goal["monthly_income"])
    actual_income_received = (
        float(month_incomes["amount"].sum()) if not month_incomes.empty else 0.0
    )
    total_income = fixed_income + actual_income_received

    # Calculation of savings/expenses
    savings_goal = float(goal["target_savings"])
    total_spent = (
        float(month_expenses["amount"].sum()) if not month_expenses.empty else 0.0
    )
    current_savings_estimate = total_income - total_spent

    # Category summary breakdown
    category_summary = ""
    if not month_expenses.empty:
        category_totals = month_expenses.groupby("category")["amount"].sum()
        for cat, amt in category_totals.items():
            category_summary += f"- {cat}: ₹{amt:.2f}\n"
    else:
        category_summary = "- No expenses recorded yet for this month.\n"

    # Recent 10 expenses details
    recent_summary = ""
    if not month_expenses.empty:
        # Sort descending by date and ID to get latest 10
        recent_10 = month_expenses.sort_values(
            by=["date", "id"], ascending=[False, False]
        ).head(10)
        for _, row in recent_10.iterrows():
            date_str = row["date"].strftime("%d/%m/%Y")
            desc = row["description"]
            cat = row["category"]
            amt = row["amount"]
            ref = f" | Reflection: {row['reflection']}" if row.get("reflection") else ""
            recent_summary += f"- {date_str}: ₹{amt:.2f} | {desc} ({cat}){ref}\n"
    else:
        recent_summary = "- No recent transactions logged.\n"

    context_str = (
        f"Month: {selected_date.strftime('%B %Y')}\n"
        f"Financial Stats Summary:\n"
        f"- Fixed Planned Monthly Income: ₹{fixed_income:.2f}\n"
        f"- Additional Income Received: ₹{actual_income_received:.2f}\n"
        f"- Total Income (Planned + Received): ₹{total_income:.2f}\n"
        f"- Target Savings Goal: ₹{savings_goal:.2f}\n"
        f"- Current Savings Estimate (Total Income - Total Spent): ₹{current_savings_estimate:.2f}\n"
        f"- Total Expenses Logged: ₹{total_spent:.2f}\n\n"
        f"Category Spending Breakdown:\n{category_summary}\n"
        f"Latest 10 Transactions:\n{recent_summary}"
    )

    return context_str
