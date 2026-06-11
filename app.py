from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from database import (
    CATEGORIES,
    INCOME_SOURCES,
    add_expense,
    add_income,
    delete_expense,
    delete_income,
    get_expenses,
    get_incomes,
    get_goal,
    init_db,
    save_goal,
)
from insights import currency, generate_insights


st.set_page_config(page_title="KakeiboAI", page_icon="₹", layout="wide")


def category_color(category):
    return {
        "Survival (Needs)": "#2F80ED",
        "Optional (Wants)": "#F2994A",
        "Culture (Growth & Learning)": "#27AE60",
        "Extra (Unexpected)": "#EB5757",
    }.get(category, "#828282")


def current_month_items(rows):
    if rows.empty:
        return rows
    today = pd.Timestamp.today()
    return rows[
        (rows["date"].dt.month == today.month) & (rows["date"].dt.year == today.year)
    ]


def money_input_value(value):
    return "₹ " if float(value) == 0 else f"₹ {int(value)}"


def parse_money_input(value):
    cleaned_value = value.strip().replace(",", "").replace("₹", "").replace(" ", "")
    if not cleaned_value:
        return 0.0
    if not cleaned_value.isdigit():
        return None
    return float(cleaned_value)


init_db()
goal = get_goal()
expenses = get_expenses()
incomes = get_incomes()
month_expenses = current_month_items(expenses)
month_incomes = current_month_items(incomes)

actual_income_received = float(month_incomes["amount"].sum()) if not month_incomes.empty else 0

total_spent = float(month_expenses["amount"].sum()) if not month_expenses.empty else 0
planned_spend = max(float(goal["monthly_income"]) - float(goal["target_savings"]), 0)
remaining_budget = planned_spend - total_spent
forecast_savings = float(goal["monthly_income"]) - total_spent
progress = (
    0
    if goal["target_savings"] <= 0
    else max(0, min(forecast_savings / goal["target_savings"], 1))
)

current_month_label = pd.Timestamp.today().strftime("%B %Y")

header_left, header_right = st.columns([0.72, 0.28], vertical_alignment="center")
with header_left:
    st.title("KakeiboAI")
    st.caption("Reflect. Save. Grow.")
with header_right:
    st.metric("Current Month", current_month_label)

plan_panel, income_panel, expense_panel = st.columns([0.85, 0.95, 1.1], gap="large")

with plan_panel:
    with st.container(border=True):
        st.subheader("Monthly Plan")
        with st.form("goal_form"):
            monthly_income_input = st.text_input(
                "Fixed Monthly Income",
                value=money_input_value(goal["monthly_income"]),
                placeholder="₹ 20000",
            )
            target_savings_input = st.text_input(
                "Savings goal",
                value=money_input_value(goal["target_savings"]),
                placeholder="₹ 3000",
            )
            save_plan = st.form_submit_button("Save plan", width="stretch")
            if save_plan:
                monthly_income = parse_money_input(monthly_income_input)
                target_savings = parse_money_input(target_savings_input)
                if monthly_income is None or target_savings is None:
                    st.error("Use numbers only for income and savings goal.")
                elif target_savings > monthly_income:
                    st.error("Savings goal cannot be higher than monthly income.")
                else:
                    save_goal(monthly_income, target_savings)
                    st.success("Monthly plan saved.")
                    st.rerun()

with income_panel:
    with st.container(border=True):
        st.subheader("Quick Income")
        with st.form("income_form", clear_on_submit=True):
            income_cols = st.columns([0.95, 0.95, 1.25])
            with income_cols[0]:
                income_amount_input = st.text_input("Amount", placeholder="₹ 2000")
            with income_cols[1]:
                income_date = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
            with income_cols[2]:
                income_source = st.selectbox("Source", INCOME_SOURCES, index=0)

            custom_source = ""
            if income_source == "Other":
                custom_source = st.text_input("Custom source", placeholder="Freelance, gift, etc.")

            income_notes = st.text_input(
                "Notes",
                placeholder="Rent for June, bonus payout, interest earned",
            )

            income_submitted = st.form_submit_button("Add income", width="stretch")
            if income_submitted:
                income_amount = parse_money_input(income_amount_input)
                source_text = custom_source.strip() if income_source == "Other" else income_source
                if income_amount is None:
                    st.error("Use numbers only for income amount.")
                elif income_amount <= 0:
                    st.error("Enter an amount greater than zero.")
                elif not source_text:
                    st.error("Choose or enter an income source.")
                else:
                    add_income(income_amount, income_date, source_text, income_notes)
                    st.success("Income added.")
                    st.rerun()

with expense_panel:
    with st.container(border=True):
        st.subheader("Quick Expense")
        with st.form("expense_form", clear_on_submit=True):
            expense_cols = st.columns([0.8, 0.8, 1.35])
            with expense_cols[0]:
                expense_amount_input = st.text_input("Amount", placeholder="₹ 250")
            with expense_cols[1]:
                expense_date = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
            with expense_cols[2]:
                category = st.selectbox("Kakeibo category", CATEGORIES, index=None)
            description = st.text_input(
                "Description",
                placeholder="Coffee, bus pass, online course",
            )

            reflection = ""
            if category in {"Optional (Wants)", "Extra (Unexpected)"}:
                reflection = st.text_area(
                    "Reflection",
                    placeholder="Was this planned, necessary, or worth delaying?",
                )

            submitted = st.form_submit_button("Add expense", width="stretch")
            if submitted:
                expense_amount = parse_money_input(expense_amount_input)
                if expense_amount is None:
                    st.error("Use numbers only for expense amount.")
                elif expense_amount <= 0:
                    st.error("Enter an amount greater than zero.")
                elif category is None:
                    st.error("Choose one of the four Kakeibo categories.")
                elif not description.strip():
                    st.error("Add a short description.")
                else:
                    add_expense(expense_amount, expense_date, category, description, reflection)
                    st.success("Expense added.")
                    st.rerun()

st.divider()

metric_cols = st.columns(5)
metric_cols[0].metric("Monthly Income", currency(goal["monthly_income"]))
metric_cols[1].metric("Income Received", currency(actual_income_received))
metric_cols[2].metric("Savings Goal", currency(goal["target_savings"]))
metric_cols[3].metric("Spent This Month", currency(total_spent))
metric_cols[4].metric("Budget Left", currency(remaining_budget))

st.progress(progress, text=f"Projected savings: {currency(forecast_savings)}")

if goal["monthly_income"] <= 0:
    st.info("Add your monthly plan to unlock savings status.")
elif forecast_savings >= goal["target_savings"]:
    st.success("Savings status: On track")
elif remaining_budget < 0:
    st.error("Savings status: Over planned spending budget")
else:
    st.warning("Savings status: Needs attention")

dashboard_left, dashboard_right = st.columns([1.35, 0.85], gap="large")

with dashboard_left:
    with st.container(border=True):
        st.subheader("Spending Dashboard")
        if month_expenses.empty:
            st.info("No expenses yet for this month. Add one from Quick Expense to start the dashboard.")
        else:
            category_totals = (
                month_expenses.groupby("category", as_index=False)["amount"].sum()
                .sort_values("amount", ascending=False)
            )

            chart_col, table_col = st.columns([1.15, 0.85], gap="medium")
            with chart_col:
                chart = px.pie(
                    category_totals,
                    values="amount",
                    names="category",
                    hole=0.48,
                    color="category",
                    color_discrete_map={category: category_color(category) for category in CATEGORIES},
                )
                chart.update_traces(textposition="inside", textinfo="percent+label")
                chart.update_layout(
                    showlegend=False,
                    margin=dict(l=0, r=0, t=10, b=10),
                    height=350,
                )
                st.plotly_chart(chart, width="stretch")

            with table_col:
                st.markdown("**Category Totals**")
                table = category_totals.rename(
                    columns={"category": "Kakeibo Category", "amount": "Amount"}
                )
                table["Amount"] = table["Amount"].map(currency)
                st.dataframe(table, hide_index=True, width="stretch")

with dashboard_right:
    with st.container(border=True):
        st.subheader("AI Coach")
        for insight in generate_insights(
            month_expenses,
            float(goal["monthly_income"]),
            float(goal["target_savings"]),
        ):
            st.info(insight)

        st.subheader("Monthly Review")
        if month_expenses.empty:
            st.write("Your review will appear after you add expenses.")
        else:
            optional_extra = month_expenses[
                month_expenses["category"].isin(["Optional (Wants)", "Extra (Unexpected)"])
            ]["amount"].sum()
            st.write(f"Total spending: **{currency(total_spent)}**")
            st.write(f"Optional + Extra spending: **{currency(optional_extra)}**")
            if forecast_savings >= goal["target_savings"]:
                st.success("On track")
            else:
                st.warning("Needs attention")

st.subheader("Income History")
if incomes.empty:
    st.write("No saved incomes yet.")
else:
    income_history = incomes.copy()
    income_history["date"] = income_history["date"].dt.strftime("%d/%m/%Y")
    income_history["amount"] = income_history["amount"].map(currency)
    st.dataframe(
        income_history.rename(
            columns={
                "date": "Date",
                "time": "Time",
                "source": "Source",
                "amount": "Amount",
                "notes": "Notes",
            }
        )[["Date", "Time", "Source", "Amount", "Notes"]],
        hide_index=True,
        width="stretch",
    )
    st.write(income_history.columns.tolist())
    for _, row in income_history.iterrows():
        cols = st.columns([1.0, 0.8, 1.0, 0.8, 1.3, 0.6])
        cols[0].write(row["date"])
        cols[1].write(row["time"])
        cols[2].write(row["Source"])
        cols[3].write(row["Amount"])
        cols[4].write(row["Notes"])
        if cols[5].button("Delete", key=f"delete_income_{row['id']}"):
            st.session_state.pending_delete = {
                "type": "income",
                "id": int(row["id"]),
                "summary": f"{row['Source']} - {row['Amount']} on {row['date']}",
            }

if st.session_state.get("pending_delete") and st.session_state["pending_delete"]["type"] == "income":
    with st.modal("Confirm delete income"):
        st.warning(
            f"Are you sure you want to delete this income entry?\n\n{st.session_state['pending_delete']['summary']}"
        )
        if st.button("Yes, delete income", key="confirm_delete_income"):
            delete_income(st.session_state["pending_delete"]["id"])
            del st.session_state["pending_delete"]
            st.success("Income entry deleted.")
            st.experimental_rerun()
        if st.button("Cancel", key="cancel_delete_income"):
            del st.session_state["pending_delete"]

st.subheader("Expense History")
if expenses.empty:
    st.write("No saved expenses yet.")
else:
    history = expenses.copy()
    history["date"] = history["date"].dt.strftime("%d/%m/%Y")
    history["amount"] = history["amount"].map(currency)
    st.dataframe(
        history.rename(
            columns={
                "date": "date",
                "time": "Time",
                "description": "Description",
                "category": "Category",
                "amount": "Amount",
                "reflection": "Reflection",
            }
        )[["date", "Time", "Description", "Category", "Amount", "Reflection"]],
        hide_index=True,
        width="stretch",
    )

    for _, row in history.iterrows():
        cols = st.columns([0.9, 0.7, 1.4, 0.9, 0.8, 0.8, 0.6])
        cols[0].write(row["Date"])
        cols[1].write(row["time"])
        cols[2].write(row["Description"])
        cols[3].write(row["Category"])
        cols[4].write(row["Amount"])
        cols[5].write(row["Reflection"])
        if cols[6].button("Delete", key=f"delete_expense_{row['id']}"):
            st.session_state.pending_delete = {
                "type": "expense",
                "id": int(row["id"]),
                "summary": f"{row['Description']} - {row['Amount']} on {row['Date']}",
            }

if st.session_state.get("pending_delete") and st.session_state["pending_delete"]["type"] == "expense":
    with st.modal("Confirm delete expense"):
        st.warning(
            f"Are you sure you want to delete this expense entry?\n\n{st.session_state['pending_delete']['summary']}"
        )
        if st.button("Yes, delete expense", key="confirm_delete_expense"):
            delete_expense(st.session_state["pending_delete"]["id"])
            del st.session_state["pending_delete"]
            st.success("Expense entry deleted.")
            st.experimental_rerun()
        if st.button("Cancel", key="cancel_delete_expense"):
            del st.session_state["pending_delete"]
