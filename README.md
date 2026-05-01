# HK Student Budget Assistant

A text-based personal budget and spending tracker built for university students in Hong Kong.
Runs entirely in the terminal. All data is stored locally in CSV and JSON files — nothing leaves your machine.

**COMP1110 Group Project — Topic A: Personal Budget and Spending Assistant**
School of Computing and Data Science, The University of Hong Kong, Semester 2 2025–2026

---

## Requirements

- Python 3.10 or later
- No external libraries required (uses stdlib only)

---

## How to Run

### Option 1 — Explore with sample data (recommended for TAs)

```bash
python seed_data.py
python main.py
```

`seed_data.py` writes a sample profile, balances, 6 budget rules, and 27 transactions so all features are immediately visible without manual entry.

### Option 2 — Fresh start

```bash
python main.py
```

The setup wizard launches automatically on first run. Follow the prompts to configure your profile, categories, budget rules, and account balances.

---

## Running the Test Cases

```bash
python test_cases.py
```

Runs 12 documented test cases covering normal flows and edge cases. All should print `[PASS]`.

---

## Reproducing the Case Studies

Each case study has its own folder under `case_studies/` containing a `transactions.csv` and `rules.csv`.

**Steps to reproduce any scenario:**

```bash
# 1. Copy the scenario files into the project root (replace existing files)
cp case_studies/scenario1/transactions.csv .
cp case_studies/scenario1/rules.csv .

# 2. Set up a matching config and balances
python seed_data.py

# 3. Run the app
python main.py
```

Replace `scenario1` with `scenario2`, `scenario3`, or `scenario4` as needed.

| Folder | Scenario | Key feature tested |
|---|---|---|
| `scenario1/` | Daily food budget — HKD 50/day cap | Daily cap alert, want/need split |
| `scenario2/` | Monthly transport tracker — HKD 600/month | Credit exclusion from totals, % threshold alert |
| `scenario3/` | Subscription creep detection | Cap breach + % threshold + uncategorized alert firing together |
| `scenario4/` | Zero spending edge case + late allowance | Zero-spend summaries, credit handling, minimum-value transaction |

**What to check on the dashboard for each scenario:**

- `scenario1` — Food & Dining percentage alert (92.4% of spending)
- `scenario2` — Transport percentage alert (67.0% of spending), no cap breach yet
- `scenario3` — Subscriptions cap breach (over by HKD 96), 51.3% alert, 3 uncategorized warnings
- `scenario4` — Housing percentage alert (65.2%), credits excluded from HKD 997.01 total

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

## File Reference

| File | Purpose |
|---|---|
| `main.py` | Entry point. Loads all data, runs the main menu loop, coordinates all modules. |
| `data.py` | All file I/O. Reads/writes `transactions.csv`, `rules.csv`, `balances.json`, `config.json`. |
| `transactions.py` | Transaction logic: add-transaction flow, want/need classification, all filter/query functions. |
| `summaries.py` | Statistics and reporting: category breakdowns, trend analysis, monthly/daily totals, all report views. |
| `rules.py` | Budget rule engine: checks rules against transaction data, prints alerts, manages the rules menu. |
| `setup.py` | First-run wizard and post-setup helpers. |
| `utils.py` | Shared helpers: validated input prompts, amount/date formatting, terminal output utilities. |
| `seed_data.py` | One-time data seeder for exploration. Safe to delete after use. |
| `test_cases.py` | 12 documented automated test cases. Run with `python test_cases.py`. |

---

## Data Files (auto-generated, gitignored)

| File | Format | Contents |
|---|---|---|
| `config.json` | JSON | Profile, debit categories, income categories, want/need lists, account names |
| `transactions.csv` | CSV | All transactions: date, amount, category, account, description, type, direction |
| `rules.csv` | CSV | Budget rules: category, limit amount, period |
| `balances.json` | JSON | Current balance per account |

These files are excluded from the repository via `.gitignore` as they contain personal runtime data. They are generated automatically on first run or by `seed_data.py`.

---

## Input Validation

All prompts validate input and re-ask on bad values — the app will never crash from invalid input:
- Dates must be `YYYY-MM-DD`
- Amounts must be numeric and greater than 0
- Menu choices must be a listed number
- Required fields cannot be left blank
- Malformed rows in CSV files are silently skipped on load

---

## Alert Types

The rule engine supports three alert types, all visible on the main menu dashboard:

| Alert | Trigger |
|---|---|
| Cap breach | Category spending exceeds its defined daily/weekly/monthly limit |
| Percentage threshold | A category exceeds 30% of total spending in the current period |
| Uncategorized warning | One or more transactions have a blank or "Other" category |
