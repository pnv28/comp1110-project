"""Budget rule management and alert checking."""

from datetime import date
from data import load_rules, save_rules
from transactions import filter_by_period, total_spent, filter_by_category
from utils import (
    header, section, divider, fmt_amount,
    prompt, prompt_required, prompt_float, prompt_choice,
    prompt_yes_no, prompt_int, pause
)

PERIODS = ["daily", "weekly", "monthly"]


# ── Alert checking ────────────────────────────────────────────────────────────

def check_rules(transactions: list[dict],
                rules: list[dict],
                ref_date: date | None = None) -> list[dict]:
    """
    Return a list of alert dicts for any breached rules.
    Each alert: {category, limit, period, spent, overspent}
    """
    alerts = []
    today = ref_date or date.today()
    for rule in rules:
        cat_txns = filter_by_category(transactions, rule["category"])
        period_txns = filter_by_period(cat_txns, rule["period"], today)
        spent = total_spent(period_txns)
        if spent > rule["limit_amount"]:
            alerts.append({
                "category": rule["category"],
                "limit": rule["limit_amount"],
                "period": rule["period"],
                "spent": spent,
                "overspent": round(spent - rule["limit_amount"], 2),
            })
    return alerts


def print_alerts(alerts: list[dict]) -> None:
    """Print budget breach warnings. Call after every new transaction."""
    if not alerts:
        return
    print("\n" + "!" * 60)
    print("  ⚠  BUDGET ALERT")
    print("!" * 60)
    for a in alerts:
        print(f"\n  Category : {a['category']}")
        print(f"  Period   : {a['period'].capitalize()}")
        print(f"  Limit    : {fmt_amount(a['limit'])}")
        print(f"  Spent    : {fmt_amount(a['spent'])}")
        print(f"  Overspent: {fmt_amount(a['overspent'])}  ← over budget!")
    print("\n" + "!" * 60)


def check_and_print_alerts(transactions: list[dict],
                            rules: list[dict]) -> None:
    alerts = check_rules(transactions, rules)
    print_alerts(alerts)


# ── CRUD for rules ────────────────────────────────────────────────────────────

def view_rules(rules: list[dict]) -> None:
    print(header("Budget Rules"))
    if not rules:
        print("  No rules set yet. Add one from this menu.")
        pause()
        return
    print(f"  {'Category':<22}{'Limit':>12}  Period")
    print(f"  {divider()}")
    for i, r in enumerate(rules, 1):
        print(f"  {i:>2}. {r['category']:<20}{fmt_amount(r['limit_amount']):>12}  "
              f"per {r['period']}")
    pause()


def add_rule(rules: list[dict], cfg: dict) -> list[dict]:
    print(header("Add Budget Rule"))
    categories = cfg.get("categories", [])
    category = prompt_choice("Category", categories, allow_new=True)

    # Remove existing rule for this category
    existing = [r for r in rules if r["category"] == category]
    if existing:
        print(f"  Existing rule: {fmt_amount(existing[0]['limit_amount'])} / {existing[0]['period']}")
        if not prompt_yes_no("  Overwrite?", default=True):
            return rules
        rules = [r for r in rules if r["category"] != category]

    limit = prompt_float(f"Spending limit for '{category}' (HKD)")
    period = prompt_choice("Period", PERIODS, default="monthly")

    rules.append({"category": category, "limit_amount": limit, "period": period})
    save_rules(rules)
    print(f"\n  Rule added: {category} — {fmt_amount(limit)} per {period}.")
    pause()
    return rules


def remove_rule(rules: list[dict]) -> list[dict]:
    print(header("Remove Budget Rule"))
    if not rules:
        print("  No rules to remove.")
        pause()
        return rules
    for i, r in enumerate(rules, 1):
        print(f"  {i}. {r['category']}  —  {fmt_amount(r['limit_amount'])} / {r['period']}")
    idx = prompt_int("Rule number to remove", 1, len(rules)) - 1
    removed = rules.pop(idx)
    save_rules(rules)
    print(f"  Removed rule for '{removed['category']}'.")
    pause()
    return rules


def manage_rules_menu(rules: list[dict], transactions: list[dict], cfg: dict) -> list[dict]:
    while True:
        print(header("Budget Rules"))
        print("  1. View all rules")
        print("  2. Add / update rule")
        print("  3. Remove rule")
        print("  4. Check current status")
        print("  5. Back")
        choice = input("\n  > ").strip()
        if choice == "1":
            view_rules(rules)
        elif choice == "2":
            rules = add_rule(rules, cfg)
        elif choice == "3":
            rules = remove_rule(rules)
        elif choice == "4":
            _print_rule_status(rules, transactions)
        elif choice == "5":
            break
    return rules


def _print_rule_status(rules: list[dict], transactions: list[dict]) -> None:
    print(header("Budget Status — Current Period"))
    if not rules:
        print("  No rules set.")
        pause()
        return
    today = date.today()
    print(f"  {'Category':<22}{'Limit':>12}{'Spent':>12}{'Remaining':>12}  Period  Status")
    print(f"  {divider()}")
    for r in rules:
        cat_txns = filter_by_category(transactions, r["category"])
        period_txns = filter_by_period(cat_txns, r["period"], today)
        spent = total_spent(period_txns)
        remaining = r["limit_amount"] - spent
        status = "OK" if remaining >= 0 else "OVER"
        marker = "⚠ " if status == "OVER" else "✓ "
        print(f"  {r['category']:<22}{fmt_amount(r['limit_amount']):>12}"
              f"{fmt_amount(spent):>12}{fmt_amount(remaining):>12}"
              f"  {r['period']:<8} {marker}{status}")
    pause()
