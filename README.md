# KakeiboAI

### Reflect. Save. Grow.

KakeiboAI is an AI-powered personal finance companion inspired by the century-old Japanese **Kakeibo** budgeting methodology. Unlike traditional expense trackers that focus solely on recording transactions, KakeiboAI helps users understand **why** they spend money and build healthier financial habits through reflection, goal setting, and intelligent insights.

### Frontend Link: https://kakeibo-ai.streamlit.app/
---

## Problem Statement

Many students and young professionals struggle with:

* Impulsive spending
* Poor budgeting habits
* Difficulty achieving savings goals
* Lack of awareness about spending patterns

Traditional budgeting applications provide charts and statistics but rarely help users understand the motivations behind their spending decisions.

---

## Solution

KakeiboAI digitizes the Japanese Kakeibo method and enhances it with AI-powered insights.

The platform encourages users to:

* Track income and expenses
* Set monthly savings goals
* Categorize spending
* Reflect on purchases
* Receive personalized financial recommendations

By combining financial tracking with behavioral reflection, KakeiboAI helps users make more intentional spending decisions.

---

## Core Philosophy

Every month, users answer four key questions:

1. How much money do I have?
2. How much would I like to save?
3. How much am I spending?
4. How can I improve?

KakeiboAI transforms these questions into a guided digital experience.

---
## What Makes KakeiboAI Different?

Most expense trackers answer:
"Where did my money go?"

KakeiboAI answers:
"Why did I spend my money this way?"

Instead of focusing solely on transactions and analytics, KakeiboAI encourages users to reflect on spending decisions, identify behavioral patterns, and make intentional financial choices.

## Features

### Expense Tracking

Record daily expenses quickly and easily.

### Savings Goal Management

Set monthly savings targets and monitor progress in real time.

### Kakeibo Categories

Expenses are categorized into:

* Survival (Needs)
* Optional (Wants)
* Culture (Learning & Growth)
* Extra (Unexpected Expenses)

### Reflection Journal

Users are encouraged to reflect on purchases through prompts such as:

* Was this purchase necessary?
* Could it have been delayed?
* Did it provide lasting value?

### AI Financial Coach

KakeiboAI analyzes spending behavior and generates intelligent financial insights using spending patterns, budgeting rules, and AI-assisted recommendations.

Examples:
- "You spent 35% more on food delivery this week than usual."
- "Your current spending trend may cause you to miss your savings target."
- "Most of your discretionary spending occurs during weekends."
- "Reducing food delivery expenses by two orders this month could increase savings by ₹700."

### Monthly Review

Analyze spending patterns and identify opportunities for improvement.

### Interactive Financial Dashboard

Visualize spending trends, category-wise breakdowns, savings progress, and monthly summaries through interactive charts and analytics.

---

## Example User Journey

1. Set monthly income or allowance
2. Define savings goal
3. Record expenses throughout the month
4. Categorize purchases
5. Receive AI-generated insights
6. Complete monthly reflections
7. Improve spending habits over time
## Sample Scenario

Monthly Allowance: ₹12,000
Savings Goal: ₹3,000

Expenses:
- Swiggy: ₹350
- Coffee: ₹180
- Online Course: ₹500

AI Insight:
"You have spent 42% of your discretionary budget within the first two weeks. Reducing food delivery expenses could help you achieve your savings goal."

Reflection Prompt:
"Was this purchase planned or impulsive?"
---

## Tech Stack

### Application Framework

- Frontend: Streamlit
- Backend: Python

### Database

- SQLite
- Supabase for Feedback collection

### Data Processing & Analytics

- Pandas
- NumPy

### Data Visualization

- Plotly

### AI Agents

- Ollama (Local)
- Google Gemini (BYOK)

### Development Tools

- Git
- GitLab
- VS Code

### Deployment

- Streamlit Community Cloud
- Local deployment for hackathon demonstration

## Run Locally

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
streamlit run app.py
```

The app stores data locally in `kakeibo.db`, which is ignored by Git.

## Future Scope

- Personalized AI Financial Advisor
- Bank Account Integration
- Receipt Scanning using OCR
- Voice-Based Expense Logging
- Financial Wellness Scoring
- Shared Budgeting for Families and Groups

---

## Why KakeiboAI?

Most finance applications track transactions.

**KakeiboAI tracks financial behavior.**

Our goal is to help users develop mindful spending habits, achieve savings goals, and build long-term financial well-being through reflection and awareness.

---

## Hackathon Project

Built as part of Hackathon 2 under Swecha Internship- Summer of 2026.

---

### Tagline

**Track Less. Understand More.**

## Security

Please refer to [SECURITY.md](SECURITY.md) for information about reporting vulnerabilities and responsible disclosure.

## Installation

### Prerequisites

* Python 3.10+
* pip
* Git

### Clone the Repository

```bash
git clone <repository-url>
cd kakeiboAI
```

### Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

## Usage

### Set Your Monthly Plan

1. Enter your monthly income.
2. Set a savings goal.
3. Save your plan.

### Record Expenses

1. Navigate to the expense section.
2. Enter amount, category, description, and reflection.
3. Submit to save the expense.

### Record Income

1. Navigate to the income section.
2. Enter amount, source, and notes.
3. Submit to save the income record.

### Review Insights

* View monthly spending trends.
* Monitor savings progress.
* Receive AI-generated financial insights.
* Analyze spending patterns across categories.

### Change Language

Use the language selector in the sidebar to switch between:

* English
* हिन्दी (Hindi)
* मराठी (Marathi)
* తెలుగు (Telugu)

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/my-feature
```

3. Commit your changes.

```bash
git commit -m "feat: add my feature"
```

4. Push your branch.

```bash
git push origin feature/my-feature
```

5. Open a Pull Request describing your changes.

Please ensure code changes are tested and documented before submission.

---

## AI Features

KakeiboAI includes an AI assistant that analyzes your monthly spending and offers Kakeibo-based mindful financial advice. You can chat with it dynamically or trigger predefined analysis actions.

### Local AI Inference (Default)
We prioritize privacy and run AI inference locally.
* **Provider**: Ollama
* **Default Model**: `llama3`

To set up local inference:
1. Install [Ollama](https://ollama.com).
2. Download the `llama3` model:
   ```bash
   ollama pull llama3
   ```
3. Start the Ollama daemon:
   ```bash
   ollama serve
   ```

### Cloud AI (Gemini BYOK)
If you prefer cloud models or do not have enough GPU power to run a local model, KakeiboAI supports **Bring Your Own Key (BYOK)** for Google Gemini.
* **Provider**: Google Gemini
* **Default Model**: `gemini-1.5-flash`

### Switching Providers
1. Open the **🤖 AI Settings** panel in the Streamlit sidebar.
2. Select your preferred provider (Ollama or Gemini).
3. If you select Gemini, input your **Gemini API Key**. The key is stored in memory (`st.session_state`) and is never saved or leaked.

---

## Supabase Feedback Storage Setup

To collect and persist community feedback across Streamlit Cloud deployments, KakeiboAI integrates with Supabase as its remote data store. If Supabase is not configured, the feedback submission and analytics components will gracefully show a "Feedback service temporarily unavailable." message without interrupting the rest of the application.

### 1. Create a Supabase Project
1. Sign in to [Supabase](https://supabase.com/).
2. Click **New project** and select your organization.
3. Enter a project name, database password, and region, then click **Create new project**.

### 2. Create the Feedback Table
Navigate to the **SQL Editor** in the Supabase dashboard and run the following query to create the `feedback` table:

```sql
create table feedback (
  id bigint generated by default as identity primary key,
  user_id bigint not null,
  username text not null,
  rating int not null,
  ai_usefulness_rating int,
  comments text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
```

> [!NOTE]
> Ensure that Row Level Security (RLS) is configured appropriately. For a simple setup, you can add policies allowing **Enable Read Access** (SELECT) and **Enable Insert Access** (INSERT) for all users (`anon` and `authenticated`).

### 3. Configure Secrets
To connect KakeiboAI to your Supabase instance, create a secrets file locally:

1. Inside the root of your project directory, create a folder named `.streamlit` if it does not exist.
2. Create a file named `secrets.toml` inside `.streamlit/`:
   ```bash
   mkdir -p .streamlit
   touch .streamlit/secrets.toml
   ```
3. Add your Supabase credentials to `.streamlit/secrets.toml`:
   ```toml
   SUPABASE_URL = "https://your-project-ref.supabase.co"
   SUPABASE_ANON_KEY = "your-anon-key-here"
   ```

> [!IMPORTANT]
> Never commit `.streamlit/secrets.toml` to Git. The `.gitignore` file of this repository is pre-configured to ignore this folder.
> When deploying to **Streamlit Community Cloud**, navigate to your app settings, click on **Secrets**, and paste the two lines of TOML config there.
