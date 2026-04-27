"""Programmatic test cases for the budgeting app."""

import csv
import os
import sys
import tempfile
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import data
from transactions import total_spent, filter_by_period, classify
from rules import check_rules
from summaries import category_breakdown, want_need_split
from utils import validate_amount

_CSV_HEADER = "date,amount,category,account,description,type,direction\n"
_GOOD_ROW   = "2026-04-15,50.00,Food & Dining,HSBC,Lunch,need,debit\n"
_BAD_DATE   = "not-a-date,30.00,Transport,Cash,,need,debit\n"


def _ok(label: str, passed: bool) -> None:
    print(f"[{'PASS' if passed else 'FAIL'}] {label}")


def run_all_tests() -> None:
    print("=" * 60)
    print("  Running all tests")
    print("=" * 60)

    _original_txn_file = data.TRANSACTIONS_FILE

    # 1. Loading from a missing file should return an empty list without crashing.
    data.TRANSACTIONS_FILE = "/tmp/__no_such_budget_file__.csv"
    _ok("Load from missing file → empty list", data.load_transactions() == [])

    # 2. A file that exists but contains only the header row should yield no transactions.
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        f.write(_CSV_HEADER)
        _tmp_empty = f.name
    data.TRANSACTIONS_FILE = _tmp_empty
    _ok("Load from empty CSV → empty list", data.load_transactions() == [])
    os.unlink(_tmp_empty)

    # 3. One malformed row (bad date) must be silently skipped; the valid row must load.
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        f.write(_CSV_HEADER)
        f.write(_GOOD_ROW)
        f.write(_BAD_DATE)
        _tmp_bad = f.name
    data.TRANSACTIONS_FILE = _tmp_bad
    loaded = data.load_transactions()
    _ok("Load CSV with malformed row → skip bad row, keep good", len(loaded) == 1)
    os.unlink(_tmp_bad)

    data.TRANSACTIONS_FILE = _original_txn_file  # restore

    # 4. validate_amount enforces amount > 0; negative values must be rejected.
    _ok(
        "Negative amount → rejected by validate_amount",
        validate_amount("-50") is False and validate_amount("50") is True,
    )

    # 5. total_spent on an empty list must return 0.0 without raising an exception.
    _ok("total_spent on empty list → 0.0", total_spent([]) == 0.0)

    # 6. Credits (income) must be excluded; only debit amounts should be summed.
    mixed = [
        {"amount": 100.0, "direction": "debit"},
        {"amount":  50.0, "direction": "credit"},
        {"amount":  75.0, "direction": "debit"},
    ]
    _ok("total_spent on debits+credits → sums debits only", total_spent(mixed) == 175.0)

    # 7. filter_by_period "daily" must return only transactions dated today.
    today = date.today()
    daily_pool = [
        {"date": today,                "amount": 10.0, "direction": "debit"},
        {"date": date(2020, 1, 1),     "amount": 20.0, "direction": "debit"},
        {"date": date(2099, 12, 31),   "amount": 30.0, "direction": "debit"},
    ]
    daily = filter_by_period(daily_pool, "daily", ref_date=today)
    _ok(
        "filter_by_period 'daily' → today's transactions only",
        len(daily) == 1 and daily[0]["date"] == today,
    )

    # 8. A category in need_categories must be classified as "need".
    cfg_needs = {"need_categories": ["Food & Dining", "Transport"]}
    _ok("classify known need category → 'need'", classify("Food & Dining", cfg_needs) == "need")

    # 9. A category absent from need_categories must default to "want".
    _ok("classify unknown category → 'want' (default)", classify("Video Games", cfg_needs) == "want")

    # 10. When spending is below the cap, check_rules must return no alerts.
    txns_low  = [{"date": today, "amount": 30.0, "category": "Food & Dining", "direction": "debit"}]
    rules_low = [{"category": "Food & Dining", "limit_amount": 100.0, "period": "daily"}]
    cap_alerts = [a for a in check_rules(txns_low, rules_low, ref_date=today)
                  if a.get("type", "cap") == "cap"]
    _ok("check_rules under limit → no cap alerts", cap_alerts == [])

    # 11. When spending exceeds the cap, the alert must report the exact overspent amount.
    txns_high  = [{"date": today, "amount": 150.0, "category": "Food & Dining", "direction": "debit"}]
    rules_high = [{"category": "Food & Dining", "limit_amount": 100.0, "period": "daily"}]
    cap_alerts_high = [a for a in check_rules(txns_high, rules_high, ref_date=today)
                       if a.get("type", "cap") == "cap"]
    _ok(
        "check_rules over limit → one alert, correct overspent amount",
        len(cap_alerts_high) == 1
        and cap_alerts_high[0]["category"] == "Food & Dining"
        and cap_alerts_high[0]["overspent"] == 50.0,
    )

    # 12. All summary functions must handle an empty transaction list without crashing.
    bd  = category_breakdown([])
    wns = want_need_split([])
    _ok(
        "Zero spending across all categories → summaries return 0, no crash",
        bd == {} and wns == (0.0, 0.0),
    )

    print("=" * 60)
    print("  All tests complete.")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
