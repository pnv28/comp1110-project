# Code Documentation — HK Student Budget Assistant

This document explains every module, class, function, data structure, and design decision in the codebase.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Data Structures](#2-data-structures)
3. [Module: `data.py`](#3-module-datapy)
4. [Module: `utils.py`](#4-module-utilspy)
5. [Module: `setup.py`](#5-module-setuppy)
6. [Module: `transactions.py`](#6-module-transactionspy)
7. [Module: `rules.py`](#7-module-rulespy)
8. [Module: `summaries.py`](#8-module-summariespy)
9. [Module: `main.py`](#9-module-mainpy)
10. [Module: `seed_data.py`](#10-module-seed_datapy)
11. [Data Flow](#11-data-flow)
12. [Key Design Decisions](#12-key-design-decisions)

---

## 1. Project Structure

```
comp1110-project/
├── main.py           # Entry point and main menu loop
├── data.py           # All file I/O (CSV and JSON)
├── utils.py          # Shared input/output helpers
├── setup.py          # First-run setup wizard and settings helpers
├── transactions.py   # Transaction logic and query functions
├── rules.py          # Budget rule engine and alerts
├── summaries.py      # Reports and statistics
├── seed_data.py      # One-time sample data generator
│
├── config.json       # (generated) User profile and app config
├── transactions.csv  # (generated) All transaction records
├── rules.csv         # (generated) Budget rules
└── balances.json     # (generated) Current account balances
```

All generated data files are gitignored. The app never needs an internet connection — everything is local.

---

## 2. Data Structures

### Transaction (dict)

The core unit of data. Every transaction is a Python dict with these keys:

| Key | Type | Description |
|---|---|---|
| `date` | `datetime.date` | Date of the transaction (in memory); `YYYY-MM-DD` string in CSV |
| `amount` | `float` | Positive value in HKD |
| `category` | `str` | Spending or income category |
| `account` | `str` | Account name (e.g. "HSBC", "Octopus") |
| `description` | `str` | Optional free-text note; empty string if omitted |
| `type` | `str` | `"want"` or `"need"` for debits; `""` for credits |
| `direction` | `str` | `"debit"` (money out) or `"credit"` (money in) |

Transactions are kept in a flat `list[dict]` sorted by insertion order (oldest first). There is no ID field — position in the list is not relied upon for logic.

---

### Rule (dict)

Defines a spending cap for one category over one period.

| Key | Type | Description |
|---|---|---|
| `category` | `str` | Must match a category in `config["categories"]` |
| `limit_amount` | `float` | Maximum allowed spend in HKD |
| `period` | `str` | `"daily"`, `"weekly"`, or `"monthly"` |

Multiple rules can exist for the same category with different periods (e.g. a monthly cap and a daily cap on Food & Dining).

---

### Config (dict, stored in `config.json`)

Persisted as JSON. Contains all user preferences.

| Key | Type | Description |
|---|---|---|
| `name` | `str` | User's display name |
| `university` | `str` | Optional; not used in logic |
| `categories` | `list[str]` | Ordered list of debit (spending) categories |
| `want_categories` | `list[str]` | Subset of categories classified as "want" |
| `need_categories` | `list[str]` | Subset of categories classified as "need" |
| `credit_categories` | `list[str]` | Income categories used for credit transactions |
| `accounts` | `list[str]` | Ordered list of account names |
| `setup_complete` | `bool` | `True` once setup has run at least once |

---

### Balances (dict, stored in `balances.json`)

Simple `{account_name: float}` mapping. Keys match the names in `config["accounts"]`. Updated every time a transaction is saved.

---

## 3. Module: `data.py`

Owns all file I/O. Every other module calls this to load or persist data. No business logic lives here.

### Constants

```python
BASE_DIR          # Absolute path to the project directory
TRANSACTIONS_FILE # BASE_DIR/transactions.csv
RULES_FILE        # BASE_DIR/rules.csv
BALANCES_FILE     # BASE_DIR/balances.json
CONFIG_FILE       # BASE_DIR/config.json

TRANSACTION_FIELDS = ["date", "amount", "category", "account",
                       "description", "type", "direction"]
RULE_FIELDS        = ["category", "limit_amount", "period"]
```

`BASE_DIR` uses `os.path.abspath(__file__)` so the files are always created relative to `data.py`, not the working directory of whoever runs the script.

---

### `load_config() -> dict`

Reads `config.json`. Returns an empty dict `{}` if the file does not exist (used by `is_first_run()`).

### `save_config(cfg: dict) -> None`

Writes the entire config dict to `config.json` with 2-space indentation.

### `is_first_run() -> bool`

Returns `True` if `config["setup_complete"]` is missing or `False`. Called once at startup in `main.py`.

---

### `_parse_transaction(row: dict) -> dict`

Private helper. Converts a raw CSV row (all strings) into a typed transaction dict:
- `date` → `datetime.date` via `strptime`
- `amount` → `float`
- `direction` → defaults to `"debit"` if the column is missing (backwards compatibility with old CSV files)

### `load_transactions() -> list[dict]`

Reads all rows from `transactions.csv`. Skips malformed rows silently (catches `ValueError` and `KeyError`). Returns `[]` if file does not exist.

### `save_transactions(transactions: list[dict]) -> None`

Overwrites `transactions.csv` completely. Converts `date` back to `YYYY-MM-DD` string and formats `amount` to 2 decimal places.

### `append_transaction(transaction: dict, transactions: list[dict]) -> list[dict]`

Appends one transaction to the in-memory list, then calls `save_transactions` to persist. Returns the updated list.

---

### `load_rules() -> list[dict]`

Reads `rules.csv`. Converts `limit_amount` to float. Skips malformed rows. Returns `[]` if file does not exist.

### `save_rules(rules: list[dict]) -> None`

Overwrites `rules.csv`. Formats `limit_amount` to 2 decimal places.

---

### `load_balances() -> dict[str, float]`

Reads `balances.json`. Returns `{}` if file does not exist.

### `save_balances(balances: dict[str, float]) -> None`

Overwrites `balances.json` with 2-space indentation.

---

## 4. Module: `utils.py`

Shared terminal I/O utilities used by every other module. Contains no business logic and no file I/O.

### Formatting

#### `fmt_amount(amount: float) -> str`
Returns a string like `"HKD 1,234.50"`. Uses comma-thousands separator.

#### `fmt_date(d: date) -> str`
Returns `"YYYY-MM-DD"` string.

#### `divider(char="─", width=60) -> str`
Returns a string of `width` repetitions of `char`. Used for horizontal rules in the UI.

#### `header(title: str, width=60) -> str`
Returns a formatted block with double-line borders (`═`) above and below the title. Prepends a blank line. Used for screen headings.

#### `section(title: str, width=60) -> str`
Returns a formatted block with single-line borders (`─`). Used for sub-sections within a screen.

---

### Input Prompts

All prompt functions loop until valid input is provided. They never raise exceptions on bad input — they print an error and re-ask.

#### `DEFAULT_HINT: str`
A two-line constant printed at the top of key screens explaining the default input conventions:
- Values in `[brackets]` → press Enter to accept
- CAPITAL letter in `Y/n` → press Enter to accept

#### `prompt(msg: str, default: str = "") -> str`
Base prompt. Displays `  {msg} [{default}]: ` (suffix omitted if no default). Returns `default` if user presses Enter on an empty field.

#### `prompt_required(msg: str) -> str`
Calls `prompt` in a loop until input is non-empty. Prints `"! This field is required."` on empty input.

#### `prompt_int(msg, min_val, max_val, default=None) -> int`
Validates that input is an integer within `[min_val, max_val]`. Re-asks on non-integer or out-of-range input.

#### `prompt_float(msg, min_val=0.01, default=None) -> float`
Validates that input is a float `>= min_val`. Returns value rounded to 2 decimal places. Re-asks on bad input. Note: `min_val=0.0` is used for opening balances (allows zero).

#### `prompt_date(msg, default="") -> date`
Validates `YYYY-MM-DD` format. Defaults to today if no default provided. Returns a `datetime.date`.

#### `prompt_choice(msg, options, default="", allow_new=False) -> str`
Displays a numbered list. If `default` is in `options`, prints a hint and marks it with `← default`. If `allow_new=True`, appends an extra option `[Enter new value]`. Accepts:
- A number matching a listed option
- The option string typed directly
- If `allow_new=True`, any string not in the list is accepted as-is

#### `prompt_yes_no(msg, default=True) -> bool`
Shows `Y/n` (default True) or `y/N` (default False). Capital letter = default. Accepts `y`, `yes`, `n`, `no` (case-insensitive) or Enter for default.

#### `prompt_period(msg, default="monthly") -> str`
Thin wrapper around `prompt_choice` for the three valid periods: `"daily"`, `"weekly"`, `"monthly"`.

---

### Other Utilities

#### `validate_date_str(s: str) -> bool`
Returns `True` if `s` parses as `YYYY-MM-DD`. Not currently used in the UI flow (validation is done inline in `prompt_date`) but available for other uses.

#### `validate_amount(s: str) -> bool`
Returns `True` if `s` parses as a positive float.

#### `clear_screen() -> None`
Runs `cls` on Windows or `clear` on Unix/macOS.

#### `pause() -> None`
Prints `"  Press Enter to continue..."` and waits for input. Used at the end of every view to let the user read output before the screen clears.

---

## 5. Module: `setup.py`

Handles the first-run wizard and all post-setup configuration helpers.

### Constants

```python
DEFAULT_CATEGORIES       # 10 standard spending categories
DEFAULT_CREDIT_CATEGORIES # 7 standard income categories
DEFAULT_WANTS            # {"Entertainment", "Shopping", "Social"}
DEFAULT_NEEDS            # {"Food & Dining", "Transport", "Housing",
                         #  "Health", "Education", "Utilities"}
```

---

### `run_setup() -> dict`

The first-run (and re-run) wizard. Returns the completed config dict after saving it.

**Flow:**

1. **Profile** — prompts for `name` (required) and `university` (optional).

2. **Setup style** — single `Y/n` prompt:
   - **Default path**: sets `categories`, `want_categories`, `need_categories`, `credit_categories` to the module-level defaults. No further category prompts.
   - **Custom path**: prompts for debit categories line-by-line (minimum 3), then classifies each as want or need, then prompts for income categories (minimum 1).

3. **Budget limits** — iterates over `cfg["categories"]`. For each, asks whether to set a limit. If yes, asks for the HKD amount and period. Calls `_prompt_period(category)` for period selection. Existing rules for the same category are replaced (not duplicated). Saves with `save_rules`.

4. **Accounts** — prompts for account names and opening balances one at a time. If the user enters nothing immediately, defaults to `["Cash", "Bank"]` with 0.0 balances. Saves with `save_balances`.

5. Sets `cfg["setup_complete"] = True` and calls `save_config`.

---

### `_prompt_period(category: str) -> str`

Private helper. Shows a numbered list (Daily / Weekly / Monthly) with "Monthly" marked as default. Uses raw `input()` (not the `prompt()` wrapper) because the formatting is fixed and not configurable. Returns `"daily"`, `"weekly"`, or `"monthly"`.

---

### `update_categories(cfg: dict) -> dict`

Post-setup helper called from Settings menu. Interactive loop allowing:
- **a** — add a new category (prompts for want/need classification)
- **r** — remove by number
- **d** — done

Updates `cfg["categories"]`, `cfg["want_categories"]`, `cfg["need_categories"]` and saves config.

### `update_credit_categories(cfg: dict) -> dict`

Same pattern as `update_categories` but for `cfg["credit_categories"]`. No want/need classification (income categories are not classified).

---

## 6. Module: `transactions.py`

Handles adding transactions and all querying/filtering logic used across the app.

### `classify(category: str, cfg: dict) -> str`

Returns `"need"` if `category` is in `cfg["need_categories"]`, otherwise `"want"`. Used to auto-classify debit transactions during the add flow.

---

### `add_transaction(transactions, cfg, balances) -> tuple[list[dict], dict[str, float]]`

Main add-transaction prompt flow. Returns the updated `(transactions, balances)` tuple.

**Flow:**

1. Ask **direction**: `"Debit (expenditure)"` or `"Credit (income)"`. Default is Debit.
2. Ask **date** (default today), **amount**, **category** (list depends on direction), **account**, **description**.
3. For **debit** only: auto-classify category as want/need via `classify()`, show result, allow override.
4. Show a summary and ask for confirmation. If not confirmed, discard and return unchanged.
5. On confirm: append transaction, update balance (`-= amount` for debit, `+= amount` for credit), save both, print confirmation with new balance.

---

### Display helpers

#### `_print_transaction(t, index=None) -> None`
Private. Prints one transaction row. Format: `date  amount  category  account  DIRECTION [TYPE]`. If `index` is given, shows `[N]` prefix (not currently used in the UI but available). Prints description on a second line if present.

#### `print_transactions(transactions, limit=None) -> None`
Public. Prints a header row then calls `_print_transaction` for each. Shows newest-first (`reversed`). If `limit` is given, shows only the last N records from the list.

---

### Filter functions

All return a new list — they never mutate the input.

#### `filter_by_date_range(transactions, start, end) -> list[dict]`
Inclusive on both ends. Compares `t["date"]` (a `datetime.date`) against `start` and `end`.

#### `filter_by_category(transactions, category) -> list[dict]`
Exact string match on `t["category"]`.

#### `filter_by_account(transactions, account) -> list[dict]`
Exact string match on `t["account"]`.

#### `filter_by_period(transactions, period, ref_date=None) -> list[dict]`
Resolves a named period relative to `ref_date` (defaults to today):
- `"daily"` → today only
- `"weekly"` → Monday of the current week through today
- `"monthly"` → first day of the current month through today

Calls `filter_by_date_range` internally.

---

### `total_spent(transactions) -> float`

Sums `amount` for all transactions where `direction == "debit"`. Credit transactions are excluded so this always represents money spent, not money received. Returns a rounded float.

---

### `view_recent(transactions, cfg) -> None`

Asks how many to show (Last 10 / 20 / 30 / All), then calls `print_transactions` with the appropriate limit.

---

## 7. Module: `rules.py`

Implements the budget rule engine and the interactive rules management menu.

### `check_rules(transactions, rules, ref_date=None) -> list[dict]`

Core rule evaluation. For each rule:
1. Filter transactions to the rule's category (`filter_by_category`).
2. Filter to the rule's period (`filter_by_period`). Note: `total_spent` inside this call only counts debits, so credit transactions never inflate spending figures.
3. If `spent > limit_amount`, append an alert dict.

**Alert dict keys:**
| Key | Type | Description |
|---|---|---|
| `category` | `str` | Category name |
| `limit` | `float` | The rule's cap |
| `period` | `str` | `"daily"`, `"weekly"`, or `"monthly"` |
| `spent` | `float` | Actual amount spent in the period |
| `overspent` | `float` | `spent - limit`, i.e. how far over |

### `print_alerts(alerts) -> None`

Prints a prominent warning block for each alert. Does nothing if `alerts` is empty.

### `check_and_print_alerts(transactions, rules) -> None`

Convenience wrapper: calls `check_rules` then `print_alerts`. Called in `main.py` after every new transaction.

---

### CRUD functions

#### `view_rules(rules) -> None`
Prints all rules in a table (category, limit, period) and pauses.

#### `add_rule(rules, cfg) -> list[dict]`
Prompts for category, limit, and period. If a rule already exists for that category, shows the existing rule and asks to overwrite. Saves and returns the updated list.

#### `remove_rule(rules) -> list[dict]`
Shows the numbered list of rules and removes the one chosen by number. Saves and returns updated list.

#### `manage_rules_menu(rules, transactions, cfg) -> list[dict]`
Loop menu with options: View / Add-Update / Remove / Check-status / Back. Returns the potentially-modified rules list to the caller.

#### `_print_rule_status(rules, transactions) -> None`
Private. For each rule, evaluates current spending and prints a table row with limit, spent, remaining, and a status indicator (✓ OK or ⚠ OVER).

---

## 8. Module: `summaries.py`

Computes statistics and renders all report views. Pure computation — no file I/O.

### Category helpers

#### `category_breakdown(transactions) -> dict[str, float]`
Returns `{category: total_amount}` sorted by total descending. Does not filter by direction — callers should pre-filter to debit-only if needed. Used with `filter_by_date_range` subsets where the caller controls which transactions are included.

#### `want_need_split(transactions) -> tuple[float, float]`
Returns `(wants_total, needs_total)` based on `t["type"]`. Ignores credit transactions (which have `type == ""`).

---

### Period helpers

#### `_week_start(d: date) -> date`
Returns the Monday of the week containing `d` (`d - timedelta(days=d.weekday())`).

#### `daily_totals(transactions, start, end) -> dict[date, float]`
Returns `{date: total}` for each day in `[start, end]` that has at least one transaction.

#### `weekly_totals(transactions, start, end) -> dict[date, float]`
Returns `{week_start_date: total}` grouped by Monday of each week.

#### `monthly_totals(transactions) -> dict[str, float]`
Returns `{"YYYY-MM": total}` across all transactions, sorted by month string.

---

### Trend analysis

#### `recent_trend(transactions, ref_date=None) -> dict`

Computes two 7-day windows:
- **Last 7**: `[today-6, today]`
- **Previous 7**: `[today-13, today-7]`

Returns a dict with totals for each window, percentage change (`None` if previous window is empty or zero), date boundaries, and per-category breakdowns for both windows.

**Percentage change formula:** `(last7 - prev7) / prev7 * 100`

---

### Top N

#### `top_categories(transactions, n=3) -> list[tuple[str, float]]`
Returns the top `n` (category, total) pairs from `category_breakdown`, already sorted descending.

---

### View functions

All view functions print output and call `pause()` at the end.

#### `view_period_summary(transactions, cfg) -> None`
Prompts for a period (This month / This week / Today / Custom range / All time), filters transactions, calls `_print_period_report`.

#### `_print_period_report(transactions, cfg, label) -> None`
Private. Renders: total count, total spent, wants/needs split, bar chart category breakdown, top 3 categories.

#### `view_trend(transactions) -> None`
Calls `recent_trend`, prints both 7-day totals and % change arrow, then a bar chart for the last 7 days by category.

#### `view_monthly_history(transactions) -> None`
Calls `monthly_totals`, prints one bar-chart row per month.

#### `view_daily_breakdown(transactions) -> None`
Shows `daily_totals` for the current month with a narrower bar chart (`width=20`).

---

### Bar chart

#### `_bar(value, max_value, width=30) -> str`
Returns a string of `█` (filled) and `░` (empty) characters scaled to `width`. Used inline in all report views.

---

## 9. Module: `main.py`

Entry point and top-level orchestration. Owns the main loop and all menu routing. No business logic — just wires modules together.

### `load_all() -> tuple[dict, list[dict], list[dict], dict]`

Calls `load_config`, `load_transactions`, `load_rules`, `load_balances` and returns all four as a tuple. Called once at startup and again after setup re-runs.

---

### `manual_balance_adjustment(balances, cfg) -> dict[str, float]`

Prompts the user to pick an account and enter a new balance directly. This bypasses the transaction system — no transaction record is created. Useful for correcting drift (ATM fees, interest, manual cash adjustments). Saves and returns updated balances.

### `view_balances(balances, cfg) -> None`

Prints a table of all accounts with their current balances and a grand total.

---

### `settings_menu(cfg, rules, transactions) -> tuple[dict, list[dict]]`

Settings sub-menu loop. Options:
1. **Manage debit categories** → `setup.update_categories`
2. **Manage income categories** → `setup.update_credit_categories`
3. **Manage budget rules** → `rules.manage_rules_menu`
4. **Re-run first-time setup** → `setup.run_setup`, then reloads rules from disk with `load_rules()` to sync the in-memory list

Returns `(cfg, rules)` so the main loop can update its references.

> **Why reload rules after re-run?** `run_setup` saves rules to `rules.csv` but does not return them. Without the explicit `load_rules()` call, the in-memory `rules` list in the main loop would remain stale until the app is restarted.

---

### `summaries_menu(transactions, cfg) -> None`

Summaries sub-menu loop. Routes to views in `summaries.py` and `transactions.view_recent`.

---

### `print_dashboard(cfg, transactions, rules, balances) -> None`

Printed at the top of every main menu iteration. Shows:
- Date and user name
- This-month transaction count and total spent (debits only)
- Total account balance across all accounts
- Budget breach list (category + amount over + period) or an all-clear message

---

### `main() -> None`

The application entry point.

1. If `is_first_run()`, calls `setup.run_setup()`.
2. Calls `load_all()` to populate `cfg, transactions, rules, balances`.
3. Enters the main `while True` loop:
   - Clears the screen
   - Prints the dashboard
   - Prints the menu
   - Routes the user's choice to the appropriate function
   - Updates `transactions`, `balances`, `rules`, or `cfg` with whatever the called function returns

All state is passed explicitly between functions — there are no global variables.

---

## 10. Module: `seed_data.py`

A standalone script (not imported by anything). Run once with `python seed_data.py` to populate all four data files with realistic sample data.

**What it writes:**

| File | Contents |
|---|---|
| `config.json` | Profile for "Alex" at HKU, full default categories and credit categories, 3 accounts |
| `balances.json` | Octopus: 320, HSBC: 4850, Cash: 180 |
| `rules.csv` | 6 rules across Food & Dining (monthly + daily), Entertainment, Transport, Shopping, Social |
| `transactions.csv` | 27 records: mix of debits and credits, spread across current and previous month |

The balances represent the *current* state, not opening balances — they are set independently of the transaction history. This is intentional: the seed is meant to give you a realistic snapshot to explore, not a mathematically consistent ledger from zero.

The `d(offset)` helper generates date strings relative to today so the data always sits in the correct month/week windows regardless of when the seed is run.

---

## 11. Data Flow

### Startup

```
main()
 └── is_first_run()?
      ├── Yes → setup.run_setup()
      │          ├── save_config()
      │          ├── save_rules()
      │          └── save_balances()
      └── No  → (skip)
 └── load_all()
      ├── load_config()       → cfg
      ├── load_transactions() → transactions
      ├── load_rules()        → rules
      └── load_balances()     → balances
```

### Adding a transaction

```
transactions.add_transaction(transactions, cfg, balances)
 ├── [user input]
 ├── append_transaction(txn, transactions)
 │    └── save_transactions()
 ├── balances[account] ± amount
 └── save_balances()
     → returns (transactions, balances)

main() after add:
 └── check_and_print_alerts(transactions, rules)
      └── check_rules() → print_alerts()
```

### Budget rule check (on dashboard)

```
print_dashboard(cfg, transactions, rules, balances)
 └── check_rules(transactions, rules)
      └── for each rule:
           filter_by_category → filter_by_period → total_spent
           if spent > limit: append alert
 └── print alert list or "all clear"
```

---

## 12. Key Design Decisions

### No database
All data lives in CSV and JSON files. This keeps the project dependency-free (pure stdlib) and makes the data human-readable and easily exportable.

### Flat transaction list
Transactions are stored in insertion order in a flat list. There is no indexing, no ID field, and no in-memory index by date or category. All filtering is done with list comprehensions. At the scale of a personal finance app (hundreds to low thousands of records) this is fast enough and much simpler than maintaining any auxiliary data structure.

### Balances managed separately from transactions
Account balances in `balances.json` are updated live whenever a transaction is saved. They are not computed from the transaction history on demand. This means the balance shown is always up-to-date without scanning all transactions, and it also means you can adjust a balance without creating a transaction (for ATM withdrawals, bank fees, etc.). The trade-off is that balances can drift if the CSV is manually edited.

### `total_spent` only counts debits
The `total_spent` function explicitly filters for `direction == "debit"`. This means every summary, every rule check, and every dashboard stat reflects money *out* only. Credit (income) transactions appear in the ledger and update balances, but do not inflate spending figures.

### In-memory state passed explicitly
The main loop holds `cfg`, `transactions`, `rules`, and `balances` as local variables and passes them into every function that needs them. Functions return updated copies. There are no module-level globals or singletons. This makes data flow easy to trace and avoids hidden side-effects.

### Setup re-run reloads rules explicitly
After `setup.run_setup()` is called from the settings menu, `main.py` explicitly calls `load_rules()` to refresh the in-memory `rules` list. `run_setup` saves rules to disk but does not return them — without the reload, the in-memory list would be stale and budget alerts on the dashboard would not reflect the newly configured rules.

### Direction field added with backwards compatibility
When the `direction` field was added, `_parse_transaction` was updated to default missing values to `"debit"`. Old CSV files without a `direction` column will load correctly — all existing records are treated as debits, which matches their original intent.
