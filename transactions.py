"""Add and query transactions."""

from datetime import date, timedelta
from data import append_transaction, save_transactions
from utils import (
    header, section, divider, fmt_amount, fmt_date,
    prompt, prompt_required, prompt_float, prompt_date,
    prompt_choice, prompt_yes_no, pause
)


# ── Auto-classification ───────────────────────────────────────────────────────

def classify(category: str, cfg: dict) -> str:
    """Return 'want' or 'need' based on config; default to 'want'."""
    if category in cfg.get("need_categories", []):
        return "need"
    return "want"


# ── Add transaction ───────────────────────────────────────────────────────────

def add_transaction(transactions: list[dict], cfg: dict) -> list[dict]:
    """Prompt for transaction details, confirm, and persist."""
    print(header("Add Transaction"))

    accounts = cfg.get("accounts", ["Cash"])

    # Direction
    direction = prompt_choice("Type", ["Debit (money out)", "Credit (money in)"],
                              default="Debit (money out)")
    is_debit = direction.startswith("Debit")
    direction_key = "debit" if is_debit else "credit"

    # Date
    txn_date = prompt_date("Date (YYYY-MM-DD)", default=date.today().strftime("%Y-%m-%d"))

    # Amount
    amount = prompt_float("Amount (HKD)")

    # Category — different lists for debit vs credit
    if is_debit:
        categories = cfg.get("categories", [])
    else:
        categories = cfg.get("credit_categories", ["Salary", "Allowance", "Part-time Work",
                                                    "Gift", "Refund", "Other Income"])
    category = prompt_choice("Category", categories, allow_new=True)

    # Account
    account = prompt_choice("Account", accounts, allow_new=True)

    # Description (optional)
    description = prompt("Description (optional)")

    # Want/need only applies to debit transactions
    if is_debit:
        auto_type = classify(category, cfg)
        print(f"\n  Auto-classified as: {auto_type.upper()}")
        confirmed_type = auto_type
        if not prompt_yes_no(f"  Keep classification as '{auto_type}'?", default=True):
            confirmed_type = "need" if auto_type == "want" else "want"
            print(f"  Changed to: {confirmed_type.upper()}")
    else:
        confirmed_type = ""

    txn = {
        "date": txn_date,
        "amount": amount,
        "category": category,
        "account": account,
        "description": description,
        "type": confirmed_type,
        "direction": direction_key,
    }

    # Show summary before saving
    print(section("Transaction Summary"))
    _print_transaction(txn)

    if not prompt_yes_no("\n  Save this transaction?", default=True):
        print("  Transaction discarded.")
        pause()
        return transactions

    transactions = append_transaction(txn, transactions)
    label = "DEBIT" if is_debit else "CREDIT"
    print(f"\n  ✓ Transaction saved. ({label} · {fmt_amount(amount)} · {category})")
    return transactions


# ── Display helpers ───────────────────────────────────────────────────────────

def _print_transaction(t: dict, index: int | None = None) -> None:
    prefix = f"  [{index}] " if index is not None else "  "
    d = t["date"] if isinstance(t["date"], date) else t["date"]
    direction = t.get("direction", "debit").upper()
    txn_type = t.get("type", "")
    type_tag = f"  [{txn_type.upper()}]" if txn_type else ""
    print(f"{prefix}{fmt_date(d)}  {fmt_amount(t['amount']):<18}  "
          f"{t['category']:<20}  {t['account']:<12}  {direction}{type_tag}")
    if t.get("description"):
        print(f"       Note: {t['description']}")


def print_transactions(transactions: list[dict], limit: int | None = None) -> None:
    if not transactions:
        print("  No transactions found.")
        return
    print(f"  {'Date':<12}{'Amount':<18}{'Category':<20}{'Account':<12}  Direction")
    print(f"  {divider()}")
    shown = transactions[-limit:] if limit else transactions
    for t in reversed(shown):
        _print_transaction(t)


# ── Queries ───────────────────────────────────────────────────────────────────

def filter_by_date_range(transactions: list[dict],
                          start: date, end: date) -> list[dict]:
    return [t for t in transactions if start <= t["date"] <= end]


def filter_by_category(transactions: list[dict], category: str) -> list[dict]:
    return [t for t in transactions if t["category"] == category]


def filter_by_account(transactions: list[dict], account: str) -> list[dict]:
    return [t for t in transactions if t["account"] == account]


def filter_by_period(transactions: list[dict], period: str,
                     ref_date: date | None = None) -> list[dict]:
    """Return transactions within the given period (daily/weekly/monthly)."""
    today = ref_date or date.today()
    if period == "daily":
        return filter_by_date_range(transactions, today, today)
    if period == "weekly":
        start = today - timedelta(days=today.weekday())  # Monday
        return filter_by_date_range(transactions, start, today)
    if period == "monthly":
        start = today.replace(day=1)
        return filter_by_date_range(transactions, start, today)
    return transactions


def total_spent(transactions: list[dict]) -> float:
    return round(sum(t["amount"] for t in transactions
                     if t.get("direction", "debit") == "debit"), 2)


# ── Recent transactions view ──────────────────────────────────────────────────

def view_recent(transactions: list[dict], cfg: dict) -> None:
    print(header("Recent Transactions"))
    choices = ["Last 10", "Last 20", "Last 30", "All"]
    choice = prompt_choice("Show", choices, default="Last 10")
    limits = {"Last 10": 10, "Last 20": 20, "Last 30": 30, "All": None}
    print()
    print_transactions(transactions, limit=limits[choice])
    pause()
