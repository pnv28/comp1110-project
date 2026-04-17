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
Writes a sample profile, balances, 6 budget rules, and 27 transactions (mix of debits and credits) so you can explore all features immediately.

**2. Launch the app:**
```bash
python main.py
```
If no config file exists, the setup wizard runs automatically before showing the main menu.

---

## First-Time Setup

The setup wizard runs once on first launch (or any time you choose "Re-run first-time setup" from Settings). Steps:

1. **Your profile** — name and university
2. **Setup style** — choose between:
   - **Default** — preset categories applied instantly, no further prompts
   - **Custom** — you enter every debit category, classify each as want/need, and enter income categories from scratch
3. **Budget limits** (optional) — set a spending cap per category with a daily, weekly, or monthly period
4. **Accounts & opening balances** — name your accounts (e.g. Octopus, HSBC, Cash) and set their current balances

All settings can be updated later from the **Settings** menu.

> **Tip:** Values shown in `[brackets]` are defaults — press Enter to accept.
> In `Y/n` prompts the **CAPITAL** letter is the default (e.g. `Y/n` → Enter = Yes).

---

## Main Menu

```
1. Add transaction           — record a new debit or credit
2. View summaries & reports  — breakdowns, trends, history
3. Budget rules & alerts     — manage limits and check status
4. Account balances          — view all account balances
5. Manual balance adjustment — set an account's balance directly
6. Settings                  — categories, budget rules, re-run setup
7. Quit
```

---

### Adding a Transaction

First choose the transaction type:
- **Debit (expenditure)** — money going out; uses your spending categories
- **Credit (income)** — money coming in; uses your income categories

Then fill in:
| Field | Notes |
|---|---|
| Date | Defaults to today (`YYYY-MM-DD`) |
| Amount | HKD, must be > 0 |
| Category | Choose from your list or enter a new one |
| Account | Choose from your accounts or enter a new one |
| Description | Optional free-text note |
| Want / Need | Debit only — auto-classified from setup; you can override |

On save the account balance updates automatically (debit subtracts, credit adds) and all budget rules are checked immediately.

---

### Summaries & Reports

| Option | What it shows |
|---|---|
| Period summary | Total spent, want/need split, category breakdown with bar chart for any date range |
| 7-day trend | Last 7 days vs previous 7 days with % change and per-category bars |
| Monthly history | Total spending per calendar month with bar chart |
| Daily breakdown | Day-by-day spending for the current month |
| Recent transactions | Last 10 / 20 / 30 / all transactions |

---

### Budget Rules

Each rule defines a spending cap for a category over a daily, weekly, or monthly period.

| Option | Description |
|---|---|
| View all rules | Shows limit, period, and current status for every rule |
| Add / update rule | Set or overwrite a rule for any category |
| Remove rule | Delete a rule |
| Check current status | Table: spent vs limit vs remaining for every rule right now |

A breach warning prints automatically after any transaction that pushes a category over its limit. The dashboard also shows active breaches every time you return to the main menu.

---

### Account Balances

Displays each account with its current balance and a total. Balances update automatically whenever a transaction is saved.

### Manual Balance Adjustment

Set an account's balance directly without creating a transaction record. Use this to correct drift (e.g. after a bank transfer, ATM withdrawal, or interest credit).

---

### Settings

| Option | Description |
|---|---|
| Manage debit categories | Add or remove spending categories |
| Manage income (credit) categories | Add or remove income categories |
| Manage budget rules | Full rules menu |
| Re-run first-time setup | Walks through setup again; existing transaction data is kept |

---

## File Reference

| File | Purpose |
|---|---|
| `main.py` | Entry point. Loads all data, runs the main menu loop, coordinates all modules. |
| `data.py` | All file I/O. Reads/writes `transactions.csv`, `rules.csv`, `balances.json`, `config.json`. |
| `transactions.py` | Transaction logic: add-transaction flow, want/need classification, all filter/query functions. |
| `summaries.py` | Statistics and reporting: category breakdowns, trend analysis, monthly/daily totals, all report views. |
| `rules.py` | Budget rule engine: checks rules against transaction data, prints alerts, manages the rules menu. |
| `setup.py` | First-run wizard and post-setup helpers (`update_categories`, `update_credit_categories`). |
| `utils.py` | Shared helpers: validated input prompts, amount/date formatting, terminal output utilities. |
| `seed_data.py` | One-time data seeder. Safe to delete after use. |

---

## Data Files (auto-generated, gitignored)

| File | Format | Contents |
|---|---|---|
| `config.json` | JSON | Profile, debit categories, income categories, want/need lists, account names |
| `transactions.csv` | CSV | All transactions: date, amount, category, account, description, type, direction |
| `rules.csv` | CSV | Budget rules: category, limit amount, period |
| `balances.json` | JSON | Current balance per account |

---

## Input Validation

All prompts validate input and re-ask on bad values — the app will never crash from invalid input:
- Dates must be `YYYY-MM-DD`
- Amounts must be numeric and meet the minimum (usually > 0)
- Menu choices must be a listed number
- Required fields (e.g. name) cannot be left blank
