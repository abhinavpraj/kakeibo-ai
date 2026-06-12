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

langs = {"English": "en", "हिन्दी": "hi", "मराठी": "mr", "తెలుగు": "te"}

# Default load language to configure page title first
t = load_language("en")

st.set_page_config(page_title="KakeiboAI", page_icon="₹", layout="wide")

init_db()

# Session state initialization for authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

selected = st.sidebar.selectbox(t.get("language", "🌐 Language"), list(langs.keys()))
t = load_language(langs[selected])

# Auth check - gate the entire app
if not st.session_state["authenticated"]:
    from auth.auth_ui import render_auth_ui

    render_auth_ui()
    st.stop()

# AI Settings Section in Sidebar (only shown if logged in)
st.sidebar.divider()
st.sidebar.write(f"👤 **Logged in as:** {st.session_state['username']}")
st.sidebar.subheader(t.get("ai_settings", "🤖 AI Settings"))

st.sidebar.markdown(
    "**Ollama**: " + t.get("ollama_help", "Local/private inference") + "\n\n"
    "**Gemini**: " + t.get("gemini_help", "Bring Your Own API Key (BYOK)")
)

provider_options = ["Ollama (Local)", "Gemini (BYOK)"]
if "ai_provider" not in st.session_state:
    st.session_state["ai_provider"] = "Ollama"

default_provider_index = 0 if st.session_state["ai_provider"] == "Ollama" else 1
selected_provider_label = st.sidebar.selectbox(
    t.get("ai_provider_label", "Provider"),
    provider_options,
    index=default_provider_index,
)

st.session_state["ai_provider"] = (
    "Ollama" if selected_provider_label == "Ollama (Local)" else "Gemini"
)

if st.session_state["ai_provider"] == "Gemini":
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = ""
    st.session_state["api_key"] = st.sidebar.text_input(
        t.get("gemini_api_key_label", "Gemini API Key"),
        value=st.session_state["api_key"],
        type="password",
    )
else:
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = ""

st.sidebar.divider()
if st.sidebar.button("🚪 Logout", use_container_width=True):
    from auth.auth import logout_user

    logout_user()
    st.rerun()


if "selected_date" not in st.session_state:
    st.session_state["selected_date"] = pd.Timestamp.today().normalize()

# Initialize session state keys for inputs
if st.session_state.get("clear_income_inputs"):
    st.session_state["inc_amount"] = ""
    st.session_state["inc_custom_source"] = ""
    st.session_state["inc_notes"] = ""
    st.session_state["inc_source"] = "Salary"
    del st.session_state["clear_income_inputs"]

if st.session_state.get("clear_expense_inputs"):
    st.session_state["exp_amount"] = ""
    st.session_state["exp_desc"] = ""
    st.session_state["exp_reflection"] = ""
    st.session_state["exp_category"] = None
    del st.session_state["clear_expense_inputs"]

for key, default in [
    ("exp_amount", ""),
    ("exp_desc", ""),
    ("exp_reflection", ""),
    ("exp_category", None),
    ("inc_amount", ""),
    ("inc_custom_source", ""),
    ("inc_notes", ""),
    ("inc_source", "Salary"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []


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
        (rows["date"].dt.month == target_date.month)
        & (rows["date"].dt.year == target_date.year)
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


user_id = st.session_state["user_id"]
selected_month_key = st.session_state["selected_date"].strftime("%Y-%m")
goal = get_monthly_goal(user_id, selected_month_key)
expenses = get_expenses(user_id)
incomes = get_incomes(user_id)

month_expenses = selected_month_items(expenses, st.session_state["selected_date"])
month_incomes = selected_month_items(incomes, st.session_state["selected_date"])

actual_income_received = (
    float(month_incomes["amount"].sum()) if not month_incomes.empty else 0
)
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
    btn_left, month_label_col, btn_right = st.columns(
        [0.15, 0.7, 0.15], vertical_alignment="center"
    )
    with btn_left:
        prev_month = st.button("◀", key="prev_month", use_container_width=True)
    with month_label_col:
        st.markdown(
            f"<h4 style='text-align: center; margin: 0;'>{selected_month_label}</h4>",
            unsafe_allow_html=True,
        )
    with btn_right:
        next_month = st.button("▶", key="next_month", use_container_width=True)

    if prev_month:
        st.session_state["selected_date"] = st.session_state[
            "selected_date"
        ] - pd.DateOffset(months=1)
        st.rerun()
    if next_month:
        st.session_state["selected_date"] = st.session_state[
            "selected_date"
        ] + pd.DateOffset(months=1)
        st.rerun()

# Feedback expander (only shown if logged in)
if st.session_state.get("authenticated"):
    with st.expander("⭐ Give Feedback - Share your experience with KakeiboAI"):
        st.write("How would you rate KakeiboAI?")
        rating_idx = st.feedback("stars", key="feedback_stars")

        st.slider(
            "How useful was the AI financial coach feature?",
            min_value=1,
            max_value=5,
            value=3,
            key="feedback_usefulness",
        )

        st.text_area(
            "Comments (Optional)",
            placeholder="What did you like or what can be improved?",
            key="feedback_comments",
        )

        if st.button("Submit Feedback", key="btn_submit_feedback"):
            if rating_idx is None:
                st.error("Please select a star rating first.")
            else:
                rating = rating_idx + 1
                usefulness = st.session_state.get("feedback_usefulness", 3)
                comments = st.session_state.get("feedback_comments", "")

                from database import save_feedback

                save_feedback(user_id, rating, usefulness, comments)

                # Reset inputs in session state
                st.session_state["feedback_stars"] = None
                st.session_state["feedback_usefulness"] = 3
                st.session_state["feedback_comments"] = ""

                st.success("Thank you for your feedback!")
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
            save_plan = st.form_submit_button(
                t.get("save_plan", "Save plan"), width="stretch"
            )
            if save_plan:
                monthly_income = parse_money_input(monthly_income_input)
                target_savings = parse_money_input(target_savings_input)
                if monthly_income is None or target_savings is None:
                    st.error(
                        t.get(
                            "error_income_savings_numbers",
                            "Use numbers only for income and savings goal.",
                        )
                    )
                elif target_savings > monthly_income:
                    st.error(
                        t.get(
                            "error_savings_higher",
                            "Savings goal cannot be higher than monthly income.",
                        )
                    )
                else:
                    save_monthly_goal(
                        st.session_state["user_id"],
                        selected_month_key,
                        monthly_income,
                        target_savings,
                    )
                    st.success(
                        t.get("success_monthly_plan_saved", "Monthly plan saved.")
                    )
                    st.rerun()

with income_panel:
    with st.container(border=True):
        st.subheader(t.get("quick_income", "Quick Income"))
        income_cols = st.columns([0.95, 0.95, 1.25])
        with income_cols[0]:
            income_amount_input = st.text_input(
                t.get("amount", "Amount"),
                key="inc_amount",
                placeholder=t.get("amount_placeholder_income", "₹ 2000"),
            )
        with income_cols[1]:
            income_date = st.date_input(
                t.get("date", "Date"),
                value=default_form_date,
                format="DD/MM/YYYY",
                key="inc_date",
            )
        with income_cols[2]:
            income_source = st.selectbox(
                t.get("source", "Source"), INCOME_SOURCES, key="inc_source"
            )

        custom_source = ""
        if income_source == "Other":
            custom_source = st.text_input(
                t.get("custom_source", "Custom source"),
                key="inc_custom_source",
                placeholder=t.get("custom_source_placeholder", "Freelance, gift, etc."),
            )

        income_notes = st.text_input(
            t.get("notes", "Notes"),
            key="inc_notes",
            placeholder=t.get(
                "notes_placeholder", "Rent for June, bonus payout, interest earned"
            ),
        )

        income_submitted = st.button(
            t.get("add_income", "Add income"),
            use_container_width=True,
            key="btn_add_income",
        )
        if income_submitted:
            income_amount = parse_money_input(income_amount_input)
            source_text = (
                custom_source.strip() if income_source == "Other" else income_source
            )
            if income_amount is None:
                st.error(
                    t.get(
                        "error_income_amount_numbers",
                        "Use numbers only for income amount.",
                    )
                )
            elif income_amount <= 0:
                st.error(
                    t.get(
                        "error_amount_greater_than_zero",
                        "Enter an amount greater than zero.",
                    )
                )
            elif not source_text:
                st.error(
                    t.get(
                        "error_choose_income_source",
                        "Choose or enter an income source.",
                    )
                )
            else:
                add_income(
                    st.session_state["user_id"],
                    income_amount,
                    income_date,
                    source_text,
                    income_notes,
                )
                st.session_state["clear_income_inputs"] = True
                st.success(t.get("success_income_added", "Income added."))
                st.rerun()

with expense_panel:
    with st.container(border=True):
        st.subheader(t.get("quick_expense", "Quick Expense"))
        expense_cols = st.columns([0.8, 0.8, 1.35])
        with expense_cols[0]:
            expense_amount_input = st.text_input(
                t.get("amount", "Amount"),
                key="exp_amount",
                placeholder=t.get("amount_placeholder_expense", "₹ 250"),
            )
        with expense_cols[1]:
            expense_date = st.date_input(
                t.get("date", "Date"),
                value=default_form_date,
                format="DD/MM/YYYY",
                key="exp_date",
            )
        with expense_cols[2]:
            category = st.selectbox(
                t.get("kakeibo_category", "Kakeibo category"),
                CATEGORIES,
                index=None,
                key="exp_category",
            )
        description = st.text_input(
            t.get("description", "Description"),
            key="exp_desc",
            placeholder=t.get(
                "description_placeholder", "Coffee, bus pass, online course"
            ),
        )

        reflection = ""
        if category in {
            "Optional (Wants)",
            "Culture (Growth & Learning)",
            "Extra (Unexpected)",
        }:
            reflection = st.text_area(
                t.get("reflection", "Reflection"),
                key="exp_reflection",
                placeholder=t.get(
                    "reflection_placeholder",
                    "Was this planned, necessary, or worth delaying?",
                ),
            )

        submitted = st.button(
            t.get("add_expense", "Add expense"),
            use_container_width=True,
            key="btn_add_expense",
        )
        if submitted:
            expense_amount = parse_money_input(expense_amount_input)
            if expense_amount is None:
                st.error(
                    t.get(
                        "error_expense_amount_numbers",
                        "Use numbers only for expense amount.",
                    )
                )
            elif expense_amount <= 0:
                st.error(
                    t.get(
                        "error_amount_greater_than_zero",
                        "Enter an amount greater than zero.",
                    )
                )
            elif category is None:
                st.error(
                    t.get(
                        "error_choose_kakeibo_category",
                        "Choose one of the four Kakeibo categories.",
                    )
                )
            elif not description.strip():
                st.error(t.get("error_short_description", "Add a short description."))
            else:
                add_expense(
                    st.session_state["user_id"],
                    expense_amount,
                    expense_date,
                    category,
                    description,
                    reflection,
                )
                st.session_state["clear_expense_inputs"] = True
                st.success(t.get("success_expense_added", "Expense added."))
                st.rerun()

st.divider()

metric_cols = st.columns(6)
metric_cols[0].metric(
    t.get("monthly_income_metric", "Monthly Income"), currency(goal["monthly_income"])
)
metric_cols[1].metric(
    t.get("income_received", "Income Received"), currency(actual_income_received)
)
metric_cols[2].metric(
    t.get("total_monthly_income", "Total Monthly Income"),
    currency(total_monthly_income),
)
metric_cols[3].metric(
    t.get("savings_goal", "Savings Goal"), currency(goal["target_savings"])
)
metric_cols[4].metric(
    t.get("spent_this_month", "Spent This Month"), currency(total_spent)
)
metric_cols[5].metric(t.get("budget_left", "Budget Left"), currency(remaining_budget))

st.progress(
    progress,
    text=t.get("projected_savings", "Projected savings: {amount}").format(
        amount=currency(forecast_savings)
    ),
)

if goal["monthly_income"] <= 0:
    st.info(
        t.get(
            "info_add_monthly_plan", "Add your monthly plan to unlock savings status."
        )
    )
elif forecast_savings >= goal["target_savings"]:
    st.success(t.get("savings_status_on_track", "Savings status: On track"))
elif remaining_budget < 0:
    st.error(
        t.get(
            "savings_status_over_budget", "Savings status: Over planned spending budget"
        )
    )
else:
    st.warning(
        t.get("savings_status_needs_attention", "Savings status: Needs attention")
    )

dashboard_left, dashboard_right = st.columns([1.35, 0.85], gap="large")

with dashboard_left:
    with st.container(border=True):
        st.subheader(t.get("spending_dashboard", "Spending Dashboard"))
        if month_expenses.empty:
            st.info(
                t.get(
                    "info_no_monthly_expenses",
                    "No expenses yet for this month. Add one from Quick Expense to start the dashboard.",
                )
            )
        else:
            category_totals = (
                month_expenses.groupby("category", as_index=False)["amount"]
                .sum()
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
                    color_discrete_map={
                        category: category_color(category) for category in CATEGORIES
                    },
                )
                chart.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    insidetextorientation="horizontal",
                )
                chart.update_layout(
                    showlegend=False,
                    margin=dict(l=0, r=0, t=10, b=10),
                    height=350,
                )
                st.plotly_chart(chart, width="stretch")

            with table_col:
                st.markdown(t.get("category_totals", "**Category Totals**"))
                category_totals_display = category_totals.copy()
                category_totals_display["amount"] = category_totals_display[
                    "amount"
                ].map(currency)
                table = category_totals_display.rename(
                    columns={
                        "category": t.get("kakeibo_category", "Kakeibo Category"),
                        "amount": t.get("amount", "Amount"),
                    }
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
            st.write(
                t.get(
                    "review_placeholder",
                    "Your review will appear after you add expenses.",
                )
            )
        else:
            optional_extra = month_expenses[
                month_expenses["category"].isin(
                    ["Optional (Wants)", "Extra (Unexpected)"]
                )
            ]["amount"].sum()
            st.write(
                t.get("total_spending", "Total spending: **{amount}**").format(
                    amount=currency(total_spent)
                )
            )
            st.write(
                t.get(
                    "optional_extra_spending", "Optional + Extra spending: **{amount}**"
                ).format(amount=currency(optional_extra))
            )
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


if (
    st.session_state.get("pending_delete")
    and st.session_state["pending_delete"]["type"] == "income"
):
    with st.modal(t.get("confirm_delete_income", "Confirm delete income")):
        st.warning(
            t.get(
                "confirm_delete_income_message",
                "Are you sure you want to delete this income entry?\n\n{summary}",
            ).format(summary=st.session_state["pending_delete"]["summary"])
        )
        if st.button(
            t.get("yes_delete_income", "Yes, delete income"),
            key="confirm_delete_income",
        ):
            delete_income(
                st.session_state["user_id"], st.session_state["pending_delete"]["id"]
            )
            del st.session_state["pending_delete"]
            st.success(t.get("income_entry_deleted", "Income entry deleted."))
            st.rerun()
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

if (
    st.session_state.get("pending_delete")
    and st.session_state["pending_delete"]["type"] == "expense"
):
    with st.modal(t.get("confirm_delete_expense", "Confirm delete expense")):
        st.warning(
            t.get(
                "confirm_delete_expense_message",
                "Are you sure you want to delete this expense entry?\n\n{summary}",
            ).format(summary=st.session_state["pending_delete"]["summary"])
        )
        if st.button(
            t.get("yes_delete_expense", "Yes, delete expense"),
            key="confirm_delete_expense",
        ):
            delete_expense(
                st.session_state["user_id"], st.session_state["pending_delete"]["id"]
            )
            del st.session_state["pending_delete"]
            st.success(t.get("expense_entry_deleted", "Expense entry deleted."))
            st.rerun()
        if st.button(t.get("cancel", "Cancel"), key="cancel_delete_expense"):
            del st.session_state["pending_delete"]

# ==========================================
# COMMUNITY REVIEWS & FEEDBACK ANALYTICS
# ==========================================
st.divider()
st.subheader("💬 Community Reviews")

from database import get_feedback_stats, get_all_feedback

stats = get_feedback_stats()

if stats["total_reviews"] > 0:
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("Total Reviews", f"{stats['total_reviews']}")
    with col_stat2:
        st.metric("⭐ Average Rating", f"{stats['avg_rating']:.1f} / 5")
    with col_stat3:
        st.metric(
            "🤖 AI Usefulness Rating", f"{stats['avg_usefulness_rating']:.1f} / 5"
        )

    # Satisfaction Banner (Bonus)
    st.info(
        f"📊 **Community Satisfaction:** {stats['satisfaction_pct']:.0f}% of users rated KakeiboAI 4 stars or higher."
    )

    st.markdown("#### Recent User Reviews")
    feedback_df = get_all_feedback(limit=10)
    for _, row in feedback_df.iterrows():
        stars = "⭐" * int(row["rating"])
        comment = row["comments"]
        username = row["username"]
        try:
            created_at = pd.to_datetime(row["created_at"]).strftime("%B %Y")
        except Exception:
            created_at = str(row["created_at"])

        with st.container(border=True):
            st.markdown(f"**{stars}**")
            if comment:
                st.write(f'"{comment}"')
            st.caption(f"by {username} • {created_at}")
else:
    st.info("No feedback submitted yet. Share your experience at the top of the page!")


# ==========================================
# CHAT WITH YOUR FINANCES & QUICK ACTIONS
# ==========================================
st.divider()
st.subheader(t.get("chat_title", "🤖 Ask KakeiboAI"))

# Display active provider
active_provider_label = (
    "Local AI (Ollama)"
    if st.session_state["ai_provider"] == "Ollama"
    else "Gemini BYOK"
)
st.caption(
    f"{t.get('active_ai_engine', 'Active AI Engine:')} **{active_provider_label}**"
)

# Display example prompts
st.markdown(
    f"*{t.get('chat_examples_label', 'Try asking:')}*\n"
    f"- *How can I save more money?*\n"
    f"- *What category am I overspending in?*\n"
    f"- *Analyze my spending habits.*\n"
    f"- *Can I reach my savings goal?*"
)

# Render Quick Actions
col1, col2, col3, col4 = st.columns(4)
quick_prompt = None

with col1:
    if st.button(
        "📊 " + t.get("spending_analysis", "Spending Analysis"),
        use_container_width=True,
    ):
        quick_prompt = "Provide a detailed analysis of my spending by category, highlighting any unusual or high spending."

with col2:
    if st.button(
        "💡 " + t.get("savings_advice", "Savings Advice"), use_container_width=True
    ):
        quick_prompt = "Given my monthly income and savings goal, what actionable advice can you give me to save more money?"

with col3:
    if st.button(
        "📈 " + t.get("monthly_review", "Monthly Review"), use_container_width=True
    ):
        quick_prompt = "Provide a comprehensive review of my finances for this month, assessing if I am on track."

with col4:
    if st.button(
        "⚠️ " + t.get("spending_risks", "Spending Risks"), use_container_width=True
    ):
        quick_prompt = "Identify potential spending risks or bad habits based on my current logs and reflections."

# Handle Quick Actions trigger
if quick_prompt:
    st.session_state["chat_messages"].append(
        {"role": "user", "content": f"Request: {quick_prompt}"}
    )

    from ai.context_builder import build_financial_context

    context = build_financial_context(
        st.session_state["selected_date"], st.session_state["user_id"]
    )

    system_prompt = (
        "You are KakeiboAI, a personal finance coach based on the Japanese Kakeibo methodology (mindful spending, reflection, and saving). "
        "Use the following financial context to answer the user's request. Be encouraging, precise, and practical.\n\n"
        f"--- FINANCIAL CONTEXT ---\n{context}\n-------------------------\n\n"
        f"User Request: {quick_prompt}"
    )

    with st.spinner(t.get("ai_thinking", "KakeiboAI is thinking...")):
        from ai.provider import ask_ai

        response = ask_ai(
            provider=st.session_state["ai_provider"],
            prompt=system_prompt,
            api_key=st.session_state.get("api_key"),
        )
        st.session_state["chat_messages"].append(
            {"role": "assistant", "content": response}
        )
    st.rerun()

# Display Chat History
for message in st.session_state["chat_messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle Chat Input
user_input = st.chat_input(
    t.get("chat_input_placeholder", "Ask KakeiboAI about your finances...")
)
if user_input:
    st.session_state["chat_messages"].append({"role": "user", "content": user_input})

    from ai.context_builder import build_financial_context

    context = build_financial_context(
        st.session_state["selected_date"], st.session_state["user_id"]
    )

    system_prompt = (
        "You are KakeiboAI, a personal finance coach based on the Japanese Kakeibo methodology (mindful spending, reflection, and saving). "
        "Use the following financial context to answer the user's question. Be encouraging, precise, and practical.\n\n"
        f"--- FINANCIAL CONTEXT ---\n{context}\n-------------------------\n\n"
        f"User Question: {user_input}"
    )

    # Render user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner(t.get("ai_thinking", "KakeiboAI is thinking...")):
            from ai.provider import ask_ai

            response = ask_ai(
                provider=st.session_state["ai_provider"],
                prompt=system_prompt,
                api_key=st.session_state.get("api_key"),
            )
            st.markdown(response)

    st.session_state["chat_messages"].append({"role": "assistant", "content": response})
    st.rerun()
