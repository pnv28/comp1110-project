"""Load/save CSV and JSON config files."""

import csv
import json
import os
from datetime import date, datetime

# ── File paths ────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSACTIONS_FILE = os.path.join(BASE_DIR, "transactions.csv")
RULES_FILE = os.path.join(BASE_DIR, "rules.csv")
BALANCES_FILE = os.path.join(BASE_DIR, "balances.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

TRANSACTION_FIELDS = ["date", "amount", "category", "account", "description", "type", "direction"]
RULE_FIELDS = ["category", "limit_amount", "period"]

# ── Config ────────────────────────────────────────────────────────────────────

def load_config() -> dict:
    """Return config dict; empty dict if file missing."""
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def is_first_run() -> bool:
    cfg = load_config()
    return not cfg.get("setup_complete", False)


# ── Transactions ──────────────────────────────────────────────────────────────

def _parse_transaction(row: dict) -> dict:
    return {
        "date": datetime.strptime(row["date"], "%Y-%m-%d").date(),
        "amount": float(row["amount"]),
        "category": row["category"],
        "account": row["account"],
        "description": row.get("description", ""),
        "type": row.get("type", ""),
        "direction": row.get("direction", "debit"),
    }


def load_transactions() -> list[dict]:
    if not os.path.exists(TRANSACTIONS_FILE):
        return []
    transactions = []
    with open(TRANSACTIONS_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                transactions.append(_parse_transaction(row))
            except (ValueError, KeyError):
                pass  # skip malformed rows
    return transactions


def save_transactions(transactions: list[dict]) -> None:
    with open(TRANSACTIONS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TRANSACTION_FIELDS)
        writer.writeheader()
        for t in transactions:
            writer.writerow({
                "date": t["date"].strftime("%Y-%m-%d"),
                "amount": f"{t['amount']:.2f}",
                "category": t["category"],
                "account": t["account"],
                "description": t.get("description", ""),
                "type": t.get("type", ""),
                "direction": t.get("direction", "debit"),
            })


def append_transaction(transaction: dict, transactions: list[dict]) -> list[dict]:
    """Add transaction to list and persist."""
    transactions.append(transaction)
    save_transactions(transactions)
    return transactions


# ── Budget rules ──────────────────────────────────────────────────────────────

def load_rules() -> list[dict]:
    if not os.path.exists(RULES_FILE):
        return []
    rules = []
    with open(RULES_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rules.append({
                    "category": row["category"],
                    "limit_amount": float(row["limit_amount"]),
                    "period": row["period"],
                })
            except (ValueError, KeyError):
                pass
    return rules


def save_rules(rules: list[dict]) -> None:
    with open(RULES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RULE_FIELDS)
        writer.writeheader()
        for r in rules:
            writer.writerow({
                "category": r["category"],
                "limit_amount": f"{r['limit_amount']:.2f}",
                "period": r["period"],
            })


# ── Account balances ──────────────────────────────────────────────────────────

def load_balances() -> dict[str, float]:
    if not os.path.exists(BALANCES_FILE):
        return {}
    with open(BALANCES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_balances(balances: dict[str, float]) -> None:
    with open(BALANCES_FILE, "w", encoding="utf-8") as f:
        json.dump(balances, f, indent=2)
