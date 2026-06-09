# Feature Specification: KakeiboAI personal finance companion

**Feature Branch**: `001-kakeiboai-personal-finance-coach`

**Created**: 2026-06-09

**Status**: Draft

**Input**: User description: "AI-powered personal finance companion inspired by the Japanese Kakeibo method, focused on tracking spending, setting savings goals, categorizing expenses, reflecting on purchases, and generating intelligent financial insights.
KakeiboAI is based on the four guiding questions of the Kakeibo methodology:

1. How much money do I have?
2. How much would I like to save?
3. How much am I spending?
4. How can I improve?

These principles drive the reflection and budgeting experience throughout the application."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record and categorize expenses (Priority: P1)

A user wants to quickly log daily spending, assign it to a Kakeibo category, and see how it affects their monthly budget.

**Why this priority**: Expense tracking is the core entry point for the product and enables all subsequent insights and reflections.

**Independent Test**: Verify the user can add an expense, choose a category, and see the expense reflected in the monthly spend summary.

**Acceptance Scenarios**:

1. **Given** the user has opened the app, **when** they create a new expense with amount, category, and description, **then** the expense appears in the current month’s ledger.
2. **Given** the user has logged multiple expenses, **when** they view the expense summary, **then** category totals and remaining budget are updated correctly.

---

### User Story 2 - Set monthly savings goals and monitor progress (Priority: P1)

A user wants to define how much they want to save each month and immediately see whether current spending is on track.

**Why this priority**: Savings goal management provides a clear motivation for mindful spending and ties the product to a measurable financial result.

**Independent Test**: Confirm the user can set income and savings target, then see savings progress and a status indicator for on-track / off-track performance.

**Acceptance Scenarios**:

1. **Given** the user sets monthly income and savings target, **when** they view the dashboard, **then** savings progress and available spending budget are displayed.
2. **Given** the user logs expenses after setting a savings goal, **when** they check the dashboard, **then** the savings forecast updates based on total spending.

---

### User Story 3 - Reflect on purchases with AI-driven prompts (Priority: P2)

A user wants to understand why they spent money and whether purchases were intentional or impulsive.

**Why this priority**: Reflection distinguishes KakeiboAI from standard expense trackers by encouraging behavioral change.

**Independent Test**: Validate that reflection prompts are presented with expense details and that the user can review them in a journal-like view.

**Acceptance Scenarios**:

1. **Given** a recent expense is logged, **when** the app generates a reflection prompt, **then** the prompt asks about necessity, delayability, or value of the purchase.
2. **Given** the user answers a reflection prompt, **when** they revisit the monthly review, **then** the reflection is saved with the expense entry.

---

### User Story 4 - Generate AI financial insights from spending behavior (Priority: P2)

A user wants personalized recommendations and alerts based on category trends and budget progress.

**Why this priority**: AI insights provide value beyond raw transaction data by helping users spot patterns and avoid repeated mistakes.

**Independent Test**: Confirm the system can generate at least one insight about spending patterns and link it to user behavior.

**Acceptance Scenarios**:

1. **Given** the user has multiple expenses logged, **when** they request an insight summary, **then** the system highlights an actionable observation such as overspending in a category.
2. **Given** the user’s spending trend threatens the savings goal, **when** the dashboard updates, **then** an alert or suggestion is shown.

---

### User Story 5 - Review monthly spending and identify improvement opportunities (Priority: P3)

A user wants a concise monthly review that summarizes performance and recommends changes.

**Why this priority**: This creates a natural cadence for habit improvement and closes the loop on reflection.

**Independent Test**: Verify that the monthly review shows category breakdowns, savings progress, and suggested next steps.

**Acceptance Scenarios**:

1. **Given** a completed month of expenses, **when** the user opens the monthly review, **then** spending totals, category distribution, and savings status are displayed.
2. **Given** the review shows a gap to the goal, **when** the user reads recommendations, **then** at least one improvement suggestion is provided.

---

### Edge Cases

- What happens when the user submits an expense without a category?
- How does the system handle negative or zero amounts?
- What if the user changes the savings goal mid-month?
- How does the app behave if there is no spending data yet?
- What if the selected currency or locale is unsupported?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to record an expense with amount, date, category, description, and optional reflection.
- **FR-002**: System MUST allow users to define monthly income and savings goals.
- **FR-003**: System MUST categorize expenses using Kakeibo categories: Survival, Optional, Culture, and Extra.
- **FR-004**: System MUST calculate and display monthly savings progress, remaining budget, and category totals.
- **FR-005**: System MUST generate spending insights and recommendations based on user spending patterns, category trends, and progress toward savings goals.
- **FR-006**: System MUST provide reflection prompts tied to expense behavior.
- **FR-007**: System MUST persist user data locally using a reliable storage mechanism.
- **FR-008**: System MUST support a monthly review experience that summarizes performance and improvement opportunities.
- **FR-009:** System MUST provide an interactive dashboard with spending visualizations, category breakdowns, and savings progress indicators.

### Key Entities *(include if feature involves data)*

- **Expense**: Represents a logged transaction with amount, date, category, description, and reflection notes.
- **SavingsGoal**: Represents monthly income, target savings, and current progress.
- **Insight**: Represents an AI-generated observation or recommendation derived from spending data.
- **MonthlyReview**: Represents the summary of a month’s category spend, savings progress, and reflection outcomes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add an expense and immediately see it reflected in the monthly spending summary.
- **SC-002**: Savings progress updates correctly after any expense entry.
- **SC-003**: At least one reflection prompt or insight is generated after the user logs spending for a week.
- **SC-004**: Monthly review shows category breakdown and indicates whether the savings target is on track.
- **SC-005**: The system handles invalid expense inputs gracefully and does not crash.

## Assumptions

- Users want a lightweight personal finance tool with behavioral reflection, not a full banking app.
- The first release can ship as a web-based UI (e.g. Streamlit) backed by local persistence (SQLite).
- AI-driven insights may be generated locally or via a lightweight model; the core experience must still work without external AI access.
- Mobile-native clients are out of scope for the initial feature.
- Existing user authentication and multi-user support are out of scope for v1.
