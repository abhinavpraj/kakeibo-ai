# Implementation Plan: KakeiboAI personal finance companion

**Branch**: `001-kakeiboai` | **Date**: 2026-06-09 | **Spec**: specs/001-kakeiboai/spec.md

**Input**: Feature specification from `/specs/001-kakeiboai/spec.md`

## Summary

Build a one-day hackathon MVP for KakeiboAI with a simple Streamlit app, SQLite persistence, and rule-based financial insights. The focus is on a working demo: goal setting, expense entry, category tracking, savings progress, visualization, and lightweight insight generation.

## Technology Stack

- Python
- Streamlit
- SQLite
- Pandas
- Plotly

## Project Structure

```text
kakeiboAI/
├── app.py
├── database.py
├── insights.py
├── requirements.txt
├── kakeibo.db
└── README.md
```

## Database Schema

### Expense
- id
- amount
- date
- category
- description
- reflection

### SavingsGoal
- monthly_income
- target_savings

## Application Flow

1. User sets income
2. User sets savings goal
3. User logs expenses
4. Expenses are stored in SQLite
5. Dashboard calculates spending
6. Insights engine generates recommendations
7. Reflection prompts are displayed for discretionary expenses

## Visualization Strategy

- Category pie chart for spend distribution
- Spending summary cards for totals, budget, and savings progress
- Savings progress indicator
- Monthly overview table or chart of expenses

## Insight Engine Rules

Use simple rule-based rules in `insights.py`:

- Overspending detection: identify categories where spending exceeds expected or available budget
- Savings goal risk detection: flag when remaining savings are unlikely given current spend
- Category trend analysis: highlight categories with repeated or high discretionary spend
- Spending habit observations: surface simple patterns such as "high food/entertainment spend" or "savings goal slipping"

## One-Day Hackathon Plan

### Phase 1: Project Setup

- [ ] Create `app.py` Streamlit app entrypoint
- [ ] Add `requirements.txt` with `streamlit`, `pandas`, `plotly`
- [ ] Create minimal layout: sidebar for inputs and main area for dashboards

### Phase 2: Database & Models

- [ ] Create `database.py` with SQLite helpers and schema creation
- [ ] Implement `expenses` and `goals` tables in `kakeibo.db`
- [ ] Add basic functions to insert and read expenses/goals

### Phase 3: Expense Tracking

- [ ] Implement expense form in `app.py` with amount, date, category, description, optional reflection
- [ ] Save expenses to SQLite
- [ ] Show expense history in the app

### Phase 4: Savings Goals

- [ ] Add monthly income and savings goal inputs
- [ ] Persist goals to SQLite
- [ ] Calculate remaining budget and savings progress

### Phase 5: Dashboard & Visualizations

- [ ] Add category-wise spending pie chart
- [ ] Add summary cards for total spend, budget remaining, and savings progress
- [ ] Add a monthly overview table or simple chart

### Phase 6: Insights & Reflections

- [ ] Implement rule-based insights in `insights.py`
- [ ] Display insight messages in the dashboard
- [ ] Show reflection prompts for Optional and Extra expenses if time allows

### Phase 7: Polish & Demo Preparation

- [ ] Clean up UI labels and layout
- [ ] Verify the demo flow end-to-end
- [ ] Add run instructions to `README.md`

## Deferred Scope

The following items are explicitly out of scope for this one-day MVP:

- Authentication
- Multi-user support
- OCR
- Bank integrations
- External AI dependencies
- Mobile applications

## Notes

Keep the implementation simple and local-first. Use only the required files and minimal helper modules. Deliver a working demo rather than a complete production system.
