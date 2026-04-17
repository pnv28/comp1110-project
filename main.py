"""Entry point and main menu loop."""

import sys
from datetime import date

import data
from data import (
    load_config, load_transactions, load_rules, load_balances,
    save_config, save_balances, is_first_run
)
import setup as setup_module
from transactions import add_transaction, view_recent
from summaries import (
    view_period_summary, view_trend, view_monthly_history,
    view_daily_breakdown, view_savings_progress
)
from rules import (
    manage_rules_menu, check_and_print_alerts, check_rules, print_alerts
)
from utils import (
    header, section, divider, fmt_amount, fmt_date,
    prompt, prompt_required, prompt_float, prompt_choice,
    prompt_yes_no, pause, clear_screen
)


# ── State ─────────────────────────────────────────────────────────────────────

def load_all() -> tuple[dict, list[dict], list[dict], dict]:
    """Load and return cfg, transactions, rules, balances."""
    cfg = load_config()
    transactions = load_transactions()
    rules = load_rules()
    balances = load_balances()
    return cfg, transactions, rules, balances


# ── Balance management ────────────────────────────────────────────────────────

def manual_balance_adjustment(balances: dict[str, float], cfg: dict) -> dict[str, float]:
    print(header("Manual Balance Adjustment"))
    accounts = cfg.get("accounts", list(balances.keys()) or ["Cash"])
    if not accounts:
        accounts = ["Cash"]

    print("  Current balances:")
    for acc in accounts:
        bal = balances.get(acc, 0.0)
        print(f"    {acc:<20} {fmt_amount(bal)}")

    account = prompt_choice("Select account to update", accounts, allow_new=True)
    if account not in accounts:
        accounts.append(account)
        cfg["accounts"] = accounts
        save_config(cfg)

    current = balances.get(account, 0.0)
    print(f"  Current balance for '{account}': {fmt_amount(current)}")
    new_bal = prompt_float("New balance (HKD)", min_val=0.0, default=current)
    balances[account] = new_bal
    save_balances(balances)
    print(f"  ✓ Balance for '{account}' updated to {fmt_amount(new_bal)}.")
    pause()
    return balances


def view_balances(balances: dict[str, float], cfg: dict) -> None:
    print(header("Account Balances"))
    accounts = cfg.get("accounts", list(balances.keys()))
    if not accounts:
        print("  No accounts set up.")
    else:
        total = 0.0
        print(f"  {'Account':<24} Balance")
        print(f"  {divider()}")
        for acc in accounts:
            bal = balances.get(acc, 0.0)
            print(f"  {acc:<24} {fmt_amount(bal)}")
            total += bal
        print(f"  {divider()}")
        print(f"  {'TOTAL':<24} {fmt_amount(total)}")
    pause()


# ── Settings menu ─────────────────────────────────────────────────────────────

def settings_menu(cfg: dict, rules: list[dict],
                  transactions: list[dict]) -> tuple[dict, list[dict]]:
    while True:
        print(header("Settings"))
        print("  1. Manage categories")
        print("  2. Update savings goal")
        print("  3. Update monthly income")
        print("  4. Manage budget rules")
        print("  5. Re-run first-time setup")
        print("  6. Back")
        choice = input("\n  > ").strip()
        if choice == "1":
            cfg = setup_module.update_categories(cfg)
        elif choice == "2":
            cfg = setup_module.update_savings_goal(cfg)
        elif choice == "3":
            cfg["monthly_income"] = prompt_float(
                "Monthly income/allowance (HKD, 0 to disable)",
                min_val=0.0, default=cfg.get("monthly_income", 0.0))
            save_config(cfg)
            print("  Income updated.")
        elif choice == "4":
            rules = manage_rules_menu(rules, transactions, cfg)
        elif choice == "5":
            if prompt_yes_no("Re-run full setup? (your data is kept)", default=False):
                cfg = setup_module.run_setup()
        elif choice == "6":
            break
    return cfg, rules


# ── Summaries menu ────────────────────────────────────────────────────────────

def summaries_menu(transactions: list[dict], cfg: dict) -> None:
    while True:
        print(header("Summaries & Reports"))
        print("  1. Period summary (custom date range)")
        print("  2. 7-day trend")
        print("  3. Monthly history")
        print("  4. Daily breakdown (this month)")
        print("  5. Savings progress")
        print("  6. Recent transactions")
        print("  7. Back")
        choice = input("\n  > ").strip()
        if choice == "1":
            view_period_summary(transactions, cfg)
        elif choice == "2":
            view_trend(transactions)
        elif choice == "3":
            view_monthly_history(transactions)
        elif choice == "4":
            view_daily_breakdown(transactions)
        elif choice == "5":
            view_savings_progress(transactions, cfg)
        elif choice == "6":
            view_recent(transactions, cfg)
        elif choice == "7":
            break


# ── Dashboard (home screen) ───────────────────────────────────────────────────

def print_dashboard(cfg: dict, transactions: list[dict],
                    rules: list[dict], balances: dict[str, float]) -> None:
    today = date.today()
    name = cfg.get("name", "Student")

    print(header(f"HK Student Budget Assistant · {fmt_date(today)}"))
    print(f"  Welcome back, {name}!\n")

    # Quick stats this month
    from transactions import filter_by_period, total_spent
    month_txns = filter_by_period(transactions, "monthly", today)
    month_total = total_spent(month_txns)
    income = cfg.get("monthly_income", 0.0)

    print(f"  This month")
    print(f"    Transactions   : {len(month_txns)}")
    print(f"    Total spent    : {fmt_amount(month_total)}")
    if income > 0:
        remaining = income - month_total
        sign = "+" if remaining >= 0 else ""
        print(f"    Remaining      : {sign}{fmt_amount(remaining)}")

    # Active rule breaches
    alerts = check_rules(transactions, rules)
    if alerts:
        print(f"\n  ⚠  {len(alerts)} budget rule(s) currently breached!")
    else:
        print(f"\n  ✓  All budget rules are within limits.")

    # Account balances summary
    accs = cfg.get("accounts", [])
    if balances:
        total_bal = sum(balances.get(a, 0.0) for a in accs)
        print(f"\n  Total balance      : {fmt_amount(total_bal)}")


# ── Main menu ─────────────────────────────────────────────────────────────────

MENU = """
  ┌──────────────────────────────────────┐
  │  MAIN MENU                           │
  ├──────────────────────────────────────┤
  │  1. Add transaction                  │
  │  2. View summaries & reports         │
  │  3. Budget rules & alerts            │
  │  4. Account balances                 │
  │  5. Manual balance adjustment        │
  │  6. Settings                         │
  │  7. Quit                             │
  └──────────────────────────────────────┘
"""


def main() -> None:
    # First-run check
    if is_first_run():
        cfg = setup_module.run_setup()

    cfg, transactions, rules, balances = load_all()

    while True:
        clear_screen()
        print_dashboard(cfg, transactions, rules, balances)
        print(MENU)
        choice = input("  > ").strip()

        if choice == "1":
            transactions = add_transaction(transactions, cfg)
            # Check budget rules immediately after adding
            check_and_print_alerts(transactions, rules)
            pause()

        elif choice == "2":
            summaries_menu(transactions, cfg)

        elif choice == "3":
            rules = manage_rules_menu(rules, transactions, cfg)

        elif choice == "4":
            view_balances(balances, cfg)

        elif choice == "5":
            balances = manual_balance_adjustment(balances, cfg)

        elif choice == "6":
            cfg, rules = settings_menu(cfg, rules, transactions)

        elif choice == "7":
            print("\n  Goodbye! Keep tracking those expenses.\n")
            sys.exit(0)

        else:
            print("  ! Please enter a number from 1 to 7.")
            pause()


if __name__ == "__main__":
    main()
