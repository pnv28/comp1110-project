"""
Seed script — populates transactions.csv, rules.csv, balances.json,
and config.json with realistic sample data so you can immediately explore
summaries and test alert logic.

Run once:  python seed_data.py
"""

import json
import csv
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Config ────────────────────────────────────────────────────────────────────

config = {
    "name": "Alex",
    "university": "HKU",
    "monthly_income": 8000.0,
    "savings_goal": 1500.0,
    "savings_goal_name": "Japan trip",
    "categories": [
        "Food & Dining",
        "Transport",
        "Housing",
        "Entertainment",
        "Health",
        "Education",
        "Shopping",
        "Utilities",
        "Social",
        "Other",
    ],
    "want_categories": ["Entertainment", "Shopping", "Social"],
    "need_categories": [
        "Food & Dining", "Transport", "Housing",
        "Health", "Education", "Utilities",
    ],
    "accounts": ["Octopus", "HSBC", "Cash"],
    "setup_complete": True,
}

with open(os.path.join(BASE, "config.json"), "w") as f:
    json.dump(config, f, indent=2)

# ── Balances ──────────────────────────────────────────────────────────────────

balances = {"Octopus": 320.0, "HSBC": 4850.0, "Cash": 180.0}

with open(os.path.join(BASE, "balances.json"), "w") as f:
    json.dump(balances, f, indent=2)

# ── Budget rules ──────────────────────────────────────────────────────────────

rules = [
    {"category": "Food & Dining",  "limit_amount": "2000.00", "period": "monthly"},
    {"category": "Entertainment",  "limit_amount": "500.00",  "period": "monthly"},
    {"category": "Transport",      "limit_amount": "600.00",  "period": "monthly"},
    {"category": "Shopping",       "limit_amount": "800.00",  "period": "monthly"},
    {"category": "Social",         "limit_amount": "200.00",  "period": "weekly"},
    {"category": "Food & Dining",  "limit_amount": "80.00",   "period": "daily"},
]

with open(os.path.join(BASE, "rules.csv"), "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["category", "limit_amount", "period"])
    writer.writeheader()
    writer.writerows(rules)

# ── Transactions (25 records across ~6 weeks) ─────────────────────────────────
# Dates intentionally spread so trend and monthly history functions have data.

from datetime import date, timedelta
today = date.today()

def d(offset: int) -> str:
    """Return ISO date string relative to today."""
    return (today - timedelta(days=offset)).strftime("%Y-%m-%d")

transactions = [
    # ── This month (recent) ───────────────────────────────────────────────────
    {"date": d(0),  "amount": "42.00",  "category": "Food & Dining",  "account": "Octopus", "description": "Canteen lunch",        "type": "need"},
    {"date": d(1),  "amount": "280.00", "category": "Shopping",        "account": "HSBC",    "description": "New clothes – H&M",    "type": "want"},
    {"date": d(1),  "amount": "38.50",  "category": "Transport",       "account": "Octopus", "description": "MTR weekly top-up",    "type": "need"},
    {"date": d(2),  "amount": "65.00",  "category": "Food & Dining",   "account": "Cash",    "description": "Hotpot with friends",  "type": "need"},
    {"date": d(2),  "amount": "120.00", "category": "Social",          "account": "HSBC",    "description": "Birthday dinner",      "type": "want"},
    {"date": d(3),  "amount": "55.00",  "category": "Entertainment",   "account": "HSBC",    "description": "Netflix + Spotify",    "type": "want"},
    {"date": d(4),  "amount": "48.00",  "category": "Food & Dining",   "account": "Octopus", "description": "Breakfast + coffee",   "type": "need"},
    {"date": d(5),  "amount": "22.50",  "category": "Transport",       "account": "Octopus", "description": "Bus pass",             "type": "need"},
    {"date": d(5),  "amount": "350.00", "category": "Education",       "account": "HSBC",    "description": "Textbooks – semester", "type": "need"},
    {"date": d(6),  "amount": "89.00",  "category": "Food & Dining",   "account": "Cash",    "description": "Weekend brunch",       "type": "need"},
    {"date": d(7),  "amount": "200.00", "category": "Shopping",        "account": "HSBC",    "description": "Running shoes",        "type": "want"},
    {"date": d(7),  "amount": "75.00",  "category": "Social",          "account": "Cash",    "description": "Bar tab",              "type": "want"},
    {"date": d(8),  "amount": "150.00", "category": "Entertainment",   "account": "HSBC",    "description": "Concert tickets",      "type": "want"},
    {"date": d(9),  "amount": "62.00",  "category": "Food & Dining",   "account": "Octopus", "description": "Sushi lunch",          "type": "need"},
    {"date": d(10), "amount": "30.00",  "category": "Health",          "account": "HSBC",    "description": "Pharmacy – cold meds", "type": "need"},
    {"date": d(11), "amount": "44.00",  "category": "Food & Dining",   "account": "Octopus", "description": "Campus canteen",       "type": "need"},
    {"date": d(12), "amount": "180.00", "category": "Utilities",       "account": "HSBC",    "description": "Phone bill",           "type": "need"},
    {"date": d(13), "amount": "95.00",  "category": "Social",          "account": "HSBC",    "description": "Karaoke night",        "type": "want"},
    {"date": d(14), "amount": "520.00", "category": "Shopping",        "account": "HSBC",    "description": "AirPods (sale)",       "type": "want"},
    # ── Previous month ────────────────────────────────────────────────────────
    {"date": d(32), "amount": "1800.00","category": "Housing",         "account": "HSBC",    "description": "Monthly rent",         "type": "need"},
    {"date": d(33), "amount": "55.00",  "category": "Transport",       "account": "Octopus", "description": "MTR top-up",           "type": "need"},
    {"date": d(35), "amount": "480.00", "category": "Food & Dining",   "account": "HSBC",    "description": "Groceries (month)",    "type": "need"},
    {"date": d(38), "amount": "310.00", "category": "Entertainment",   "account": "HSBC",    "description": "Theme park – Ocean Pk","type": "want"},
    {"date": d(40), "amount": "120.00", "category": "Health",          "account": "HSBC",    "description": "Doctor visit + meds",  "type": "need"},
    {"date": d(45), "amount": "250.00", "category": "Shopping",        "account": "HSBC",    "description": "Winter jacket",        "type": "want"},
]

with open(os.path.join(BASE, "transactions.csv"), "w", newline="") as f:
    writer = csv.DictWriter(
        f, fieldnames=["date","amount","category","account","description","type"])
    writer.writeheader()
    writer.writerows(transactions)

print("✓ Sample data written:")
print(f"  config.json       — profile for 'Alex' at HKU")
print(f"  balances.json     — Octopus / HSBC / Cash")
print(f"  rules.csv         — 6 budget rules")
print(f"  transactions.csv  — {len(transactions)} transactions")
print("\nRun the app with:  python main.py")
