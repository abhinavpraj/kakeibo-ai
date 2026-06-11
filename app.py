import importlib
import sys

# Force reload database module to prevent Streamlit caching/hot-reload ImportError
if "database" in sys.modules:
    importlib.reload(sys.modules["database"])

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
    get_monthly_goal,
    init_db,
    save_monthly_goal,
)
from i18n import load_language
from insights import currency, generate_insights

langs = {
    "English": "en",
    "हिन्दी": "hi",
    "मराठी": "mr",
    "తెలుగు": "te"
}

t = load_language("en")

selected = st.sidebar.selectbox(
    t.get("language", "🌐 Language"),
    list(langs.keys())
)
t = load_language(langs[selected])


st.set_page_config(page_title=t.get("title", "KakeiboAI"), page_icon="₹", layout="wide")

if "selected_date" not in st.session_state:
    st.session_state["selected_date"] = pd.Timestamp.today().normalize()

# Initialize session state keys for inputs
for key, default in [
    ("exp_amount", ""),
    ("exp_desc", ""),
    ("exp_reflection", ""),
    ("exp_category", None),
    ("inc_amount", ""),
    ("inc_custom_source", ""),
    ("inc_notes", ""),
    ("inc_source", "Salary")
]:
    if key not in st.session_state:
        st.session_state[key] = default


def category_color(category):
    return {
        "Survival (Needs)": "#2F80ED",
        "Optional (Wants)": "#F2994A",
        "Culture (Growth & Learning)": "#27AE60",
        "Extra (Unexpected)": "#EB5757",
    }.get(category, "#828282")


def selected_month_items(rows, target_date):
    if rows.empty:
        return rows
    return rows[
        (rows["date"].dt.month == target_date.month) & (rows["date"].dt.year == target_date.year)
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
selected_month_key = st.session_state["selected_date"].strftime("%Y-%m")
goal = get_monthly_goal(selected_month_key)
expenses = get_expenses()
incomes = get_incomes()
month_expenses = selected_month_items(expenses, st.session_state["selected_date"])
month_incomes = selected_month_items(incomes, st.session_state["selected_date"])

actual_income_received = float(month_incomes["amount"].sum()) if not month_incomes.empty else 0
total_monthly_income = float(goal["monthly_income"]) + actual_income_received

total_spent = float(month_expenses["amount"].sum()) if not month_expenses.empty else 0
planned_spend = max(total_monthly_income - float(goal["target_savings"]), 0)
remaining_budget = planned_spend - total_spent

# Calculate projected savings using daily spend linear extrapolation for current month
today_date = pd.Timestamp.today()
selected_date = st.session_state["selected_date"]
if selected_date.month == today_date.month and selected_date.year == today_date.year:
    day_of_month = today_date.day
    days_in_month = today_date.days_in_month
    daily_spend = total_spent / day_of_month if day_of_month > 0 else 0
    projected_spend = daily_spend * days_in_month
    forecast_savings = total_monthly_income - projected_spend
else:
    forecast_savings = total_monthly_income - total_spent
progress = (
    0
    if goal["target_savings"] <= 0
    else max(0, min(forecast_savings / goal["target_savings"], 1))
)

selected_month_label = st.session_state["selected_date"].strftime("%B %Y")

header_left, header_right = st.columns([0.7, 0.3], vertical_alignment="center")
with header_left:
    st.title(t.get("title", "KakeiboAI"))
    st.caption(t.get("tagline", "Reflect. Save. Grow."))
with header_right:
    btn_left, month_label_col, btn_right = st.columns([0.15, 0.7, 0.15], vertical_alignment="center")
    with btn_left:
        prev_month = st.button("◀", key="prev_month", use_container_width=True)
    with month_label_col:
        st.markdown(f"<h4 style='text-align: center; margin: 0;'>{selected_month_label}</h4>", unsafe_allow_html=True)
    with btn_right:
        next_month = st.button("▶", key="next_month", use_container_width=True)

    if prev_month:
        st.session_state["selected_date"] = st.session_state["selected_date"] - pd.DateOffset(months=1)
        st.rerun()
    if next_month:
        st.session_state["selected_date"] = st.session_state["selected_date"] + pd.DateOffset(months=1)
        st.rerun()

# Calculate default form date based on the selected month
today_date = date.today()
selected_date = st.session_state["selected_date"]
if selected_date.month == today_date.month and selected_date.year == today_date.year:
    default_form_date = today_date
else:
    default_form_date = date(selected_date.year, selected_date.month, 1)

plan_panel, income_panel, expense_panel = st.columns([0.85, 0.95, 1.1], gap="large")

with plan_panel:
    with st.container(border=True):
        st.subheader(t.get("monthly_plan", "Monthly Plan"))
        with st.form("goal_form"):
            monthly_income_input = st.text_input(
                t.get("fixed_monthly_income", "Fixed Monthly Income"),
                value=money_input_value(goal["monthly_income"]),
                placeholder=t.get("fixed_monthly_income_placeholder", "₹ 20000"),
            )
            target_savings_input = st.text_input(
                t.get("savings_goal", "Savings Goal"),
                value=money_input_value(goal["target_savings"]),
                placeholder=t.get("savings_goal_placeholder", "₹ 3000"),
            )
            save_plan = st.form_submit_button(t.get("save_plan", "Save plan"), width="stretch")
            if save_plan:
                monthly_income = parse_money_input(monthly_income_input)
                target_savings = parse_money_input(target_savings_input)
                if monthly_income is None or target_savings is None:
                    st.error(t.get("error_income_savings_numbers", "Use numbers only for income and savings goal."))
                elif target_savings > monthly_income:
                    st.error(t.get("error_savings_higher", "Savings goal cannot be higher than monthly income."))
                else:
                    save_monthly_goal(selected_month_key, monthly_income, target_savings)
                    st.success(t.get("success_monthly_plan_saved", "Monthly plan saved."))
                    st.rerun()

with income_panel:
    with st.container(border=True):
        st.subheader(t.get("quick_income", "Quick Income"))
        income_cols = st.columns([0.95, 0.95, 1.25])
        with income_cols[0]:
            income_amount_input = st.text_input(t.get("amount", "Amount"), key="inc_amount", placeholder=t.get("amount_placeholder_income", "₹ 2000"))
        with income_cols[1]:
            income_date = st.date_input(t.get("date", "Date"), value=default_form_date, format="DD/MM/YYYY")
        with income_cols[2]:
            income_source = st.selectbox(t.get("source", "Source"), INCOME_SOURCES, key="inc_source")

        custom_source = ""
        if income_source == "Other":
            custom_source = st.text_input(t.get("custom_source", "Custom source"), key="inc_custom_source", placeholder=t.get("custom_source_placeholder", "Freelance, gift, etc."))

        income_notes = st.text_input(
            t.get("notes", "Notes"),
            key="inc_notes",
            placeholder=t.get("notes_placeholder", "Rent for June, bonus payout, interest earned"),
        )

        income_submitted = st.button(t.get("add_income", "Add income"), use_container_width=True)
        if income_submitted:
            income_amount = parse_money_input(income_amount_input)
            source_text = custom_source.strip() if income_source == "Other" else income_source
            if income_amount is None:
                st.error(t.get("error_income_amount_numbers", "Use numbers only for income amount."))
            elif income_amount <= 0:
                st.error(t.get("error_amount_greater_than_zero", "Enter an amount greater than zero."))
            elif not source_text:
                st.error(t.get("error_choose_income_source", "Choose or enter an income source."))
            else:
                add_income(income_amount, income_date, source_text, income_notes)
                st.success(t.get("success_income_added", "Income added."))
                st.session_state["inc_amount"] = ""
                st.session_state["inc_custom_source"] = ""
                st.session_state["inc_notes"] = ""
                st.session_state["inc_source"] = "Salary"
                st.rerun()

with expense_panel:
    with st.container(border=True):
        st.subheader(t.get("quick_expense", "Quick Expense"))
        expense_cols = st.columns([0.8, 0.8, 1.35])
        with expense_cols[0]:
            expense_amount_input = st.text_input(t.get("amount", "Amount"), key="exp_amount", placeholder=t.get("amount_placeholder_expense", "₹ 250"))
        with expense_cols[1]:
            expense_date = st.date_input(t.get("date", "Date"), value=default_form_date, format="DD/MM/YYYY")
        with expense_cols[2]:
            category = st.selectbox(t.get("kakeibo_category", "Kakeibo category"), CATEGORIES, index=None, key="exp_category")
        description = st.text_input(
            t.get("description", "Description"),
            key="exp_desc",
            placeholder=t.get("description_placeholder", "Coffee, bus pass, online course"),
        )

        reflection = ""
        if category in {"Optional (Wants)", "Culture (Growth & Learning)", "Extra (Unexpected)"}:
            reflection = st.text_area(
                t.get("reflection", "Reflection"),
                key="exp_reflection",
                placeholder=t.get("reflection_placeholder", "Was this planned, necessary, or worth delaying?"),
            )

        submitted = st.button(t.get("add_expense", "Add expense"), use_container_width=True)
        if submitted:
            expense_amount = parse_money_input(expense_amount_input)
            if expense_amount is None:
                st.error(t.get("error_expense_amount_numbers", "Use numbers only for expense amount."))
            elif expense_amount <= 0:
                st.error(t.get("error_amount_greater_than_zero", "Enter an amount greater than zero."))
            elif category is None:
                st.error(t.get("error_choose_kakeibo_category", "Choose one of the four Kakeibo categories."))
            elif not description.strip():
                st.error(t.get("error_short_description", "Add a short description."))
            else:
                add_expense(expense_amount, expense_date, category, description, reflection)
                st.success(t.get("success_expense_added", "Expense added."))
                st.session_state["exp_amount"] = ""
                st.session_state["exp_desc"] = ""
                st.session_state["exp_reflection"] = ""
                st.session_state["exp_category"] = None
                st.rerun()

st.divider()

metric_cols = st.columns(6)
metric_cols[0].metric(t.get("monthly_income_metric", "Monthly Income"), currency(goal["monthly_income"]))
metric_cols[1].metric(t.get("income_received", "Income Received"), currency(actual_income_received))
metric_cols[2].metric(t.get("total_monthly_income", "Total Monthly Income"), currency(total_monthly_income))
metric_cols[3].metric(t.get("savings_goal", "Savings Goal"), currency(goal["target_savings"]))
metric_cols[4].metric(t.get("spent_this_month", "Spent This Month"), currency(total_spent))
metric_cols[5].metric(t.get("budget_left", "Budget Left"), currency(remaining_budget))

st.progress(progress, text=t.get("projected_savings", "Projected savings: {amount}").format(amount=currency(forecast_savings)))

if goal["monthly_income"] <= 0:
    st.info(t.get("info_add_monthly_plan", "Add your monthly plan to unlock savings status."))
elif forecast_savings >= goal["target_savings"]:
    st.success(t.get("savings_status_on_track", "Savings status: On track"))
elif remaining_budget < 0:
    st.error(t.get("savings_status_over_budget", "Savings status: Over planned spending budget"))
else:
    st.warning(t.get("savings_status_needs_attention", "Savings status: Needs attention"))

dashboard_left, dashboard_right = st.columns([1.35, 0.85], gap="large")

with dashboard_left:
    with st.container(border=True):
        st.subheader(t.get("spending_dashboard", "Spending Dashboard"))
        if month_expenses.empty:
            st.info(t.get(
                "info_no_monthly_expenses",
                "No expenses yet for this month. Add one from Quick Expense to start the dashboard.",
            ))
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
                st.markdown(t.get("category_totals", "**Category Totals**"))
                category_totals_display = category_totals.copy()
                category_totals_display["amount"] = category_totals_display["amount"].map(currency)
                table = category_totals_display.rename(
                    columns={"category": t.get("kakeibo_category", "Kakeibo Category"), "amount": t.get("amount", "Amount")}
                )
                st.dataframe(table, hide_index=True, width="stretch")

with dashboard_right:
    with st.container(border=True):
        st.subheader(t.get("ai_coach", "AI Coach"))
        for insight in generate_insights(
            month_expenses,
            total_monthly_income,
            float(goal["target_savings"]),
        ):
            st.info(insight)

        st.subheader(t.get("monthly_review", "Monthly Review"))
        if month_expenses.empty:
            st.write(t.get("review_placeholder", "Your review will appear after you add expenses."))
        else:
            optional_extra = month_expenses[
                month_expenses["category"].isin(["Optional (Wants)", "Extra (Unexpected)"])
            ]["amount"].sum()
            st.write(t.get("total_spending", "Total spending: **{amount}**").format(amount=currency(total_spent)))
            st.write(t.get("optional_extra_spending", "Optional + Extra spending: **{amount}**").format(amount=currency(optional_extra)))
            if forecast_savings >= goal["target_savings"]:
                st.success(t.get("on_track", "On track"))
            else:
                st.warning(t.get("needs_attention", "Needs attention"))

st.subheader(t.get("income_history", "Income History"))
if incomes.empty:
    st.write(t.get("no_saved_incomes", "No saved incomes yet."))
else:
    income_history = incomes.copy()
    income_history["date"] = income_history["date"].dt.strftime("%d/%m/%Y")
    income_history["amount"] = income_history["amount"].map(currency)
    
    cols = ["date", "time", "source", "amount", "notes"]
    income_history_display = income_history[cols].rename(
        columns={
            "date": t.get("date", "Date"),
            "time": t.get("time", "Time"),
            "source": t.get("source", "Source"),
            "amount": t.get("amount", "Amount"),
            "notes": t.get("notes", "Notes"),
        }
    )
    st.dataframe(
        income_history_display,
        hide_index=True,
        width="stretch",
    )


if st.session_state.get("pending_delete") and st.session_state["pending_delete"]["type"] == "income":
    with st.modal(t.get("confirm_delete_income", "Confirm delete income")):
        st.warning(
            t.get(
                "confirm_delete_income_message",
                "Are you sure you want to delete this income entry?\n\n{summary}",
            ).format(summary=st.session_state["pending_delete"]["summary"])
        )
        if st.button(t.get("yes_delete_income", "Yes, delete income"), key="confirm_delete_income"):
            delete_income(st.session_state["pending_delete"]["id"])
            del st.session_state["pending_delete"]
            st.success(t.get("income_entry_deleted", "Income entry deleted."))
            st.experimental_rerun()
        if st.button(t.get("cancel", "Cancel"), key="cancel_delete_income"):
            del st.session_state["pending_delete"]

st.subheader(t.get("expense_history", "Expense History"))

if expenses.empty:
    st.write(t.get("no_saved_expenses", "No saved expenses yet."))
else:
    history = expenses.copy()
    history["date"] = history["date"].dt.strftime("%d/%m/%Y")
    history["amount"] = history["amount"].map(currency)
    
    cols = ["date", "time", "description", "category", "amount", "reflection"]
    history_display = history[cols].rename(
        columns={
            "date": t.get("date", "Date"),
            "time": t.get("time", "Time"),
            "description": t.get("description", "Description"),
            "category": t.get("category", "Category"),
            "amount": t.get("amount", "Amount"),
            "reflection": t.get("reflection", "Reflection"),
        }
    )
    st.dataframe(
        history_display,
        hide_index=True,
        width="stretch",
    )

if st.session_state.get("pending_delete") and st.session_state["pending_delete"]["type"] == "expense":
    with st.modal(t.get("confirm_delete_expense", "Confirm delete expense")):
        st.warning(
            t.get(
                "confirm_delete_expense_message",
                "Are you sure you want to delete this expense entry?\n\n{summary}",
            ).format(summary=st.session_state["pending_delete"]["summary"])
        )
        if st.button(t.get("yes_delete_expense", "Yes, delete expense"), key="confirm_delete_expense"):
            delete_expense(st.session_state["pending_delete"]["id"])
            del st.session_state["pending_delete"]
            st.success(t.get("expense_entry_deleted", "Expense entry deleted."))
            st.experimental_rerun()
        if st.button(t.get("cancel", "Cancel"), key="cancel_delete_expense"):
            del st.session_state["pending_delete"]
