# Tasks: KakeiboAI personal finance companion (Hackathon MVP)

**Input**: Design documents from `/specs/001-kakeiboai-personal-finance-coach/`

**Technology stack**: Python, Streamlit, SQLite, Pandas, Plotly

**Goal**: Build a working demo in one day for a single developer. Prioritize a functional Streamlit experience over production-grade infrastructure.

## Priority categories

**Must Have**
- Set monthly income
- Set monthly savings goal
- Add expenses
- Categorize expenses into Survival, Optional, Culture, and Extra
- Store expenses in SQLite
- View expense history
- View category-wise spending breakdown
- View savings progress
- Generate rule-based financial insights

**Should Have**
- Optional reflection prompts for Optional and Extra expenses
- Clear UI layout and summary panel

**Nice to Have**
- Simple monthly review summary
- Streamlit Cloud deployment notes

---

## Phase 1: Project Setup

**Purpose**: Get the demo scaffolded quickly.

- [ ] T001 Create a minimal `app.py` Streamlit app entrypoint.
- [ ] T002 Add `requirements.txt` with `streamlit`, `pandas`, `numpy`, and `plotly`.
- [ ] T003 Build a single-page Streamlit layout with sidebar inputs and a main dashboard area.

---

## Phase 2: Database & Models

**Purpose**: Persist goals and expenses in SQLite with minimal code.

- [ ] T004 Create SQLite schema for `expenses` and `goals` in a local `data.db` file.
- [ ] T005 Add simple database helper functions in `app.py` or `db.py` for inserting and reading records.
- [ ] T006 Define expense categories and a small helper for category validation.

---

## Phase 3: Expense Tracking

**Purpose**: Capture expenses and show history immediately.

- [ ] T007 Add expense entry controls: amount, date, category, description.
- [ ] T008 Save expense records to SQLite and reload the table after submission.
- [ ] T009 Display expense history in the main dashboard.

---

## Phase 4: Savings Goals

**Purpose**: Allow goal setting and show progress.

- [ ] T010 Add monthly income and savings goal inputs.
- [ ] T011 Persist saved goals in SQLite.
- [ ] T012 Calculate and display available spending budget and savings progress.

---

## Phase 5: Dashboard & Visualizations

**Purpose**: Turn stored data into a usable visual summary.

- [ ] T013 Add category-wise spending breakdown using Plotly charts.
- [ ] T014 Show total spending, remaining budget, and goal progress in the dashboard.
- [ ] T015 Display the current expense history and category totals on the same page.

---

## Phase 6: Insights & Reflections

**Purpose**: Add simple decision support without external AI.

- [ ] T016 Implement rule-based insights in the dashboard (e.g. overspending in a category, savings risk, high discretionary spend).
- [ ] T017 Add optional reflection prompts for Optional and Extra expenses, if time allows.

---

## Phase 7: Polish & Demo Preparation

**Purpose**: Make the app presentable and runnable.

- [ ] T018 Refine UI copy, headings, and layout in `app.py`.
- [ ] T019 Confirm the demo flow: set goals, add expenses, review dashboard and insights.
- [ ] T020 Add brief run instructions to `README.md`.

---

## Execution notes

- Keep everything in `app.py` or one small helper module for speed.
- Skip extensive tests; focus on manual verification through the Streamlit UI.
- Use SQLite for persistence, but avoid complex migration or model layers.
- Deliver a working demo with the Must Have items completed first.
