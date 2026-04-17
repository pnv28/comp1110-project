# HK Student Budget Assistant

A text-based personal budget and spending tracker built for university students in Hong Kong.
Runs entirely in the terminal. All data is stored locally in CSV and JSON files — nothing leaves your machine.

---

## Requirements

- Python 3.10 or later
- No external libraries required (uses stdlib only)

---

## Quick Start

**1. Seed sample data (optional but recommended for first-time exploration):**
```bash
python seed_data.py
```
This writes 25 sample transactions, 6 budget rules, and a sample profile so you can explore summaries and alerts immediately.

**2. Launch the app:**
```bash
python main.py
```
If no config file exists, the setup wizard runs automatically before showing the main menu.

---

## First-Time Setup

If `config.json` is missing, the app walks you through a one-time setup wizard covering:

1. Your name and university
2. Monthly income or allowance
3. Monthly savings goal and what you're saving for
4. Spending categories (use defaults or define your own)
5. Want/need classification per category
6. Optional spending limits per category
7. Account names and opening balances

You can update any of these later from **Settings** in the main menu.

---

## Main Menu

```
1. Add transaction          — record a new expense
2. View summaries & reports — breakdowns, trends, history
3. Budget rules & alerts    — manage limits and check status
4. Account balances         — view all account balances
5. Manual balance adjustment — set an account's balance directly
6. Settings                 — categories, income, goals, rules
7. Quit
```

### Adding a Transaction

You will be prompted for:
- **Date** — defaults to today, format `YYYY-MM-DD`
- **Amount** — in HKD
- **Category** — choose from your list or enter a new one
- **Account** — e.g. Octopus, HSBC, Cash
- **Description** — optional note
- **Want / Need** — auto-classified from your setup preferences; you can override

After saving, the app immediately checks all budget rules and prints a warning if any limit is breached.

### Summaries & Reports

| Option | What it shows |
|---|---|
| Period summary | Total spent, category breakdown, top 3 categories for a chosen period |
| 7-day trend | Last 7 days vs previous 7 days with % change |
| Monthly history | Total spending per calendar month |
| Daily breakdown | Day-by-day spending for the current month |
| Savings progress | Income vs spending vs your savings goal |
| Recent transactions | Last 10 / 20 / 30 / all transactions |

### Budget Rules

Each rule sets a spending limit for a category over a daily, weekly, or monthly period.
- **View all rules** — shows limit, period, and current status
- **Add / update rule** — set or overwrite a rule for any category
- **Remove rule** — delete a rule
- **Check current status** — table showing spent vs limit for every rule right now

A breach warning is printed automatically after every new transaction that pushes a category over its limit.

### Manual Balance Adjustment

Updates an account's stored balance without creating a transaction record. Use this for:
- Setting an opening balance when you first add an account
- Correcting a balance after a bank transfer or cash withdrawal

---

## File Reference

| File | Purpose |
|---|---|
| `main.py` | Entry point. Loads all data on startup, runs the main menu loop, and coordinates between modules. |
| `data.py` | All file I/O. Reads and writes `transactions.csv`, `rules.csv`, `balances.json`, and `config.json`. Every other module calls this to load or persist data. |
| `transactions.py` | Transaction logic. Handles the add-transaction prompt flow, want/need auto-classification, and filtering/querying functions used by summaries and rules. |
| `summaries.py` | Statistics and reporting. Computes category breakdowns, daily/weekly/monthly totals, the 7-day trend, savings progress, and renders all the report views. |
| `rules.py` | Budget rule engine. Checks all rules against current transaction data and prints alerts. Also provides the interactive menu for adding, removing, and viewing rules. |
| `setup.py` | First-run wizard and settings helpers. Collects profile info, categories, want/need classification, and initial budget rules. Also exposes `update_categories` and `update_savings_goal` used by the Settings menu. |
| `utils.py` | Shared helpers used across every module: input prompts with validation, date/amount formatting, re-prompt loops, and terminal output utilities. |
| `seed_data.py` | One-time data seeder. Writes sample config, balances, rules, and 25 transactions so you can test the app without entering data manually. Safe to delete after use. |

## Data Files (auto-generated)

| File | Format | Contents |
|---|---|---|
| `config.json` | JSON | User profile, categories, want/need lists, income, savings goal, account names |
| `transactions.csv` | CSV | All recorded transactions: date, amount, category, account, description, type |
| `rules.csv` | CSV | Budget rules: category, limit amount, period |
| `balances.json` | JSON | Current balance for each account |

These files are created automatically when you run the app or the seed script. They are listed in `.gitignore` so personal financial data is not accidentally committed to version control.

---

## Input Validation

All prompts validate input and re-ask on bad values — the app will never crash from invalid input:
- Dates must be in `YYYY-MM-DD` format
- Amounts must be positive numbers
- Menu choices must be a listed number; typing anything else shows an error and re-prompts
- Required fields cannot be left blank
