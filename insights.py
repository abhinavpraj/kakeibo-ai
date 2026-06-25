from database import CATEGORIES


def currency(amount):
    return f"₹{amount:,.0f}"


def generate_insights(expenses, monthly_income, target_savings):
    insights = []
    total_spent = float(expenses["amount"].sum()) if not expenses.empty else 0
    planned_spend = max(float(monthly_income) - float(target_savings), 0)
    forecast_savings = float(monthly_income) - total_spent

    if monthly_income <= 0:
        return ["Set your monthly income and savings goal to unlock personalized budget insights."]

    if expenses.empty:
        return ["Start by logging today's expenses. Kakeibo works best when spending is reviewed regularly."]

    if planned_spend and total_spent > planned_spend:
        insights.append(
            f"You have crossed your planned spending budget by {currency(total_spent - planned_spend)}. Review Optional and Extra expenses first."
        )
    elif planned_spend:
        insights.append(f"You still have {currency(planned_spend - total_spent)} available in this month's planned spending budget.")

    if forecast_savings < target_savings:
        insights.append(
            f"At the current pace, projected savings are {currency(forecast_savings)}, which is below your goal of {currency(target_savings)}."
        )
    else:
        insights.append(f"You are on track to save about {currency(forecast_savings)} this month if spending stays steady.")

    category_totals = expenses.groupby("category")["amount"].sum().to_dict()
    discretionary = category_totals.get("Optional (Wants)", 0) + category_totals.get("Extra (Unexpected)", 0)
    if total_spent and discretionary / total_spent >= 0.4:
        insights.append("Optional and Extra purchases make up a large share of spending. Add reflections to spot impulse patterns.")

    if category_totals:
        top_category = max(category_totals, key=category_totals.get)
        insights.append(f"Your highest spending category is {top_category} at {currency(category_totals[top_category])}.")

    missing_categories = [category for category in CATEGORIES if category not in category_totals]
    if missing_categories:
        insights.append(
            f"No spending recorded yet for {', '.join(missing_categories)}. That can be good, or it may mean some expenses are not logged."
        )

    return insights[:5]
