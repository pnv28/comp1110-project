"""Statistics, breakdowns, and trend analysis."""

from datetime import date, timedelta
from collections import defaultdict
from utils import (
    header, section, divider, fmt_amount, fmt_date,
    prompt_choice, prompt_date, pause
)
from transactions import (
    filter_by_date_range, filter_by_period, total_spent
)


# ── Category breakdown ────────────────────────────────────────────────────────

def category_breakdown(transactions: list[dict]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for t in transactions:
        totals[t["category"]] += t["amount"]
    return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))


def want_need_split(transactions: list[dict]) -> tuple[float, float]:
    wants = sum(t["amount"] for t in transactions if t.get("type") == "want")
    needs = sum(t["amount"] for t in transactions if t.get("type") == "need")
    return round(wants, 2), round(needs, 2)


# ── Period helpers ────────────────────────────────────────────────────────────

def _week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


def daily_totals(transactions: list[dict],
                 start: date, end: date) -> dict[date, float]:
    totals: dict[date, float] = defaultdict(float)
    for t in filter_by_date_range(transactions, start, end):
        totals[t["date"]] += t["amount"]
    return dict(sorted(totals.items()))


def weekly_totals(transactions: list[dict],
                  start: date, end: date) -> dict[date, float]:
    """Returns {week_start_date: total}."""
    totals: dict[date, float] = defaultdict(float)
    for t in filter_by_date_range(transactions, start, end):
        ws = _week_start(t["date"])
        totals[ws] += t["amount"]
    return dict(sorted(totals.items()))


def monthly_totals(transactions: list[dict]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for t in transactions:
        key = t["date"].strftime("%Y-%m")
        totals[key] += t["amount"]
    return dict(sorted(totals.items()))


# ── Trend: last 7 vs previous 7 ──────────────────────────────────────────────

def recent_trend(transactions: list[dict],
                 ref_date: date | None = None) -> dict:
    today = ref_date or date.today()
    last7_start = today - timedelta(days=6)
    prev7_start = today - timedelta(days=13)
    prev7_end   = today - timedelta(days=7)

    last7 = filter_by_date_range(transactions, last7_start, today)
    prev7 = filter_by_date_range(transactions, prev7_start, prev7_end)

    last7_total = total_spent(last7)
    prev7_total = total_spent(prev7)

    if prev7_total == 0:
        pct_change = None
    else:
        pct_change = round((last7_total - prev7_total) / prev7_total * 100, 1)

    return {
        "last7_total": last7_total,
        "prev7_total": prev7_total,
        "pct_change": pct_change,
        "last7_start": last7_start,
        "last7_end": today,
        "prev7_start": prev7_start,
        "prev7_end": prev7_end,
        "last7_by_category": category_breakdown(last7),
        "prev7_by_category": category_breakdown(prev7),
    }


# ── Top N categories ──────────────────────────────────────────────────────────

def top_categories(transactions: list[dict], n: int = 3) -> list[tuple[str, float]]:
    breakdown = category_breakdown(transactions)
    return list(breakdown.items())[:n]


# ── Savings progress ──────────────────────────────────────────────────────────

def savings_progress(transactions: list[dict], cfg: dict) -> dict:
    goal = cfg.get("savings_goal", 0.0)
    today = date.today()
    month_txns = filter_by_period(transactions, "monthly", today)
    spent = total_spent(month_txns)
    return {
        "spent": spent,
        "goal": goal,
    }


# ── Bar chart helper ──────────────────────────────────────────────────────────

def _bar(value: float, max_value: float, width: int = 30) -> str:
    if max_value == 0:
        filled = 0
    else:
        filled = int(round(value / max_value * width))
    return "█" * filled + "░" * (width - filled)


# ── View functions ────────────────────────────────────────────────────────────

def view_period_summary(transactions: list[dict], cfg: dict) -> None:
    print(header("Spending Summary"))
    options = ["This month", "This week", "Today", "Custom range", "All time"]
    choice = prompt_choice("Period", options, default="This month")

    today = date.today()
    if choice == "This month":
        start = today.replace(day=1)
        end = today
        label = today.strftime("%B %Y")
    elif choice == "This week":
        start = _week_start(today)
        end = today
        label = f"Week of {fmt_date(start)}"
    elif choice == "Today":
        start = end = today
        label = fmt_date(today)
    elif choice == "Custom range":
        start = prompt_date("Start date")
        end = prompt_date("End date")
        label = f"{fmt_date(start)} to {fmt_date(end)}"
    else:
        start = date(2000, 1, 1)
        end = today
        label = "All time"

    subset = filter_by_date_range(transactions, start, end)
    _print_period_report(subset, cfg, label)
    pause()


def _print_period_report(transactions: list[dict], cfg: dict, label: str) -> None:
    total = total_spent(transactions)
    wants, needs = want_need_split(transactions)
    top3 = top_categories(transactions, 3)
    breakdown = category_breakdown(transactions)

    print(section(f"Report: {label}"))
    print(f"  Total transactions : {len(transactions)}")
    print(f"  Total spent        : {fmt_amount(total)}")
    print(f"  Wants              : {fmt_amount(wants)}")
    print(f"  Needs              : {fmt_amount(needs)}")

    if breakdown:
        print(section("Category Breakdown"))
        max_val = max(breakdown.values()) if breakdown else 1
        for cat, amt in breakdown.items():
            bar = _bar(amt, max_val)
            pct = (amt / total * 100) if total > 0 else 0
            print(f"  {cat:<22} {bar} {fmt_amount(amt):>12}  ({pct:.1f}%)")

    if top3:
        print(section("Top 3 Categories"))
        for i, (cat, amt) in enumerate(top3, 1):
            print(f"  {i}. {cat:<22} {fmt_amount(amt)}")


def view_trend(transactions: list[dict]) -> None:
    print(header("7-Day Spending Trend"))
    trend = recent_trend(transactions)

    print(f"\n  Last 7 days  ({fmt_date(trend['last7_start'])} – {fmt_date(trend['last7_end'])})")
    print(f"    Total: {fmt_amount(trend['last7_total'])}")

    print(f"\n  Previous 7 days ({fmt_date(trend['prev7_start'])} – {fmt_date(trend['prev7_end'])})")
    print(f"    Total: {fmt_amount(trend['prev7_total'])}")

    if trend["pct_change"] is None:
        print("\n  No data for previous period to compare.")
    elif trend["pct_change"] > 0:
        print(f"\n  ▲ Spending UP {trend['pct_change']}% vs previous 7 days")
    elif trend["pct_change"] < 0:
        print(f"\n  ▼ Spending DOWN {abs(trend['pct_change'])}% vs previous 7 days")
    else:
        print("\n  ↔ Spending unchanged vs previous 7 days")

    if trend["last7_by_category"]:
        print(section("Last 7 Days by Category"))
        max_val = max(trend["last7_by_category"].values())
        for cat, amt in trend["last7_by_category"].items():
            bar = _bar(amt, max_val)
            print(f"  {cat:<22} {bar} {fmt_amount(amt):>12}")

    pause()


def view_monthly_history(transactions: list[dict]) -> None:
    print(header("Monthly Spending History"))
    mt = monthly_totals(transactions)
    if not mt:
        print("  No data yet.")
        pause()
        return
    max_val = max(mt.values())
    for month, amt in mt.items():
        bar = _bar(amt, max_val)
        print(f"  {month}  {bar} {fmt_amount(amt):>12}")
    pause()


def view_daily_breakdown(transactions: list[dict]) -> None:
    print(header("Daily Breakdown"))
    today = date.today()
    start = today.replace(day=1)
    dt = daily_totals(transactions, start, today)
    if not dt:
        print("  No transactions this month.")
        pause()
        return
    max_val = max(dt.values()) if dt else 1
    for day, amt in dt.items():
        bar = _bar(amt, max_val, width=20)
        print(f"  {fmt_date(day)}  {bar} {fmt_amount(amt):>12}")
    pause()


def view_savings_progress(transactions: list[dict], cfg: dict) -> None:
    print(header("Savings Progress"))
    sp = savings_progress(transactions, cfg)

    goal_name = cfg.get("savings_goal_name") or "Savings Goal"
    print(f"\n  Goal       : {goal_name}")
    print(f"  Spent      : {fmt_amount(sp['spent'])}")

    if sp["goal"] > 0:
        print(f"  Target     : {fmt_amount(sp['goal'])}")
    else:
        print("\n  (No savings goal set. Use Settings > Update Savings Goal.)")
    pause()
