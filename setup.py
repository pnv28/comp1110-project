"""First-run configuration flow."""

from data import load_config, save_config, save_rules, load_rules, save_balances, load_balances
from utils import (
    header, section, divider, prompt, prompt_required, prompt_float,
    prompt_yes_no, prompt_int, pause, DEFAULT_HINT
)

DEFAULT_CATEGORIES = [
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
]

DEFAULT_CREDIT_CATEGORIES = [
    "Salary",
    "Allowance",
    "Part-time Work",
    "Gift",
    "Refund",
    "Investment Return",
    "Other Income",
]

DEFAULT_WANTS = {"Entertainment", "Shopping", "Social"}
DEFAULT_NEEDS = {"Food & Dining", "Transport", "Housing", "Health", "Education", "Utilities"}


def run_setup() -> dict:
    """Interactive first-run setup. Returns completed config dict."""
    print(header("Welcome to HK Student Budget Assistant"))
    print("""
  This one-time setup will personalise the app for you.
  You can change any of these settings later from the main menu.
""")
    print(DEFAULT_HINT)
    print()

    cfg = load_config()

    # ── Step 1: Profile ───────────────────────────────────────────────────────
    print(section("Step 1 · Your Profile"))
    cfg["name"] = prompt_required("Your name")
    cfg["university"] = prompt("University (e.g. HKU, CUHK, PolyU)")

    # ── Step 2: Default or custom setup? ─────────────────────────────────────
    print(section("Step 2 · Setup Style"))
    print("  Default  — preset categories applied instantly, no extra prompts.")
    print("  Custom   — you choose every category from scratch.\n")
    use_all_defaults = prompt_yes_no("Use default setup?", default=True)

    if use_all_defaults:
        cfg["categories"]       = list(DEFAULT_CATEGORIES)
        cfg["want_categories"]  = list(DEFAULT_WANTS)
        cfg["need_categories"]  = list(DEFAULT_NEEDS)
        cfg["credit_categories"] = list(DEFAULT_CREDIT_CATEGORIES)
        print("\n  ✓ Default categories applied.")
    else:
        # Custom: spending categories
        print(section("Spending Categories"))
        print("  Enter categories one per line. Leave blank to finish.")
        print("  (You must enter at least 3)\n")
        categories = []
        while True:
            cat = prompt(f"Category {len(categories)+1}").strip()
            if not cat:
                if len(categories) >= 3:
                    break
                print("    ! Enter at least 3 categories.")
            elif cat in categories:
                print("    ! Duplicate category, skipping.")
            else:
                categories.append(cat)

        # Want/need classification
        print("\n  Classify each as 'want' or 'need' (used when adding transactions):\n")
        want_set, need_set = set(), set()
        for cat in categories:
            suggestion = ("need" if cat in DEFAULT_NEEDS else "want")
            choice = prompt(f"  '{cat}' — want or need?", default=suggestion).lower().strip()
            while choice not in ("want", "need", "w", "n"):
                choice = prompt(f"  '{cat}' — want or need?", default=suggestion).lower().strip()
            (want_set if choice in ("want", "w") else need_set).add(cat)

        cfg["categories"]      = categories
        cfg["want_categories"] = list(want_set)
        cfg["need_categories"] = list(need_set)

        # Custom: income categories
        print(section("Income Categories"))
        print("  Enter income categories one per line. Leave blank to finish.\n")
        credit_categories = []
        while True:
            cat = prompt(f"Income category {len(credit_categories)+1}").strip()
            if not cat:
                if len(credit_categories) >= 1:
                    break
                print("    ! Enter at least 1 category.")
            elif cat in credit_categories:
                print("    ! Duplicate, skipping.")
            else:
                credit_categories.append(cat)
        cfg["credit_categories"] = credit_categories

    # ── Step 3: Budget limits ─────────────────────────────────────────────────
    print(section("Step 3 · Budget Limits (optional)"))
    print("  Set a spending cap per category. Press Enter (N) to skip.\n")

    rules = load_rules()
    for cat in cfg["categories"]:
        if not prompt_yes_no(f"Set a budget limit for '{cat}'?", default=False):
            continue
        limit = prompt_float(f"Limit for '{cat}' (HKD)")
        period = _prompt_period(cat)
        rules = [r for r in rules if r["category"] != cat]
        rules.append({"category": cat, "limit_amount": limit, "period": period})
    save_rules(rules)

    # ── Step 4: Accounts ──────────────────────────────────────────────────────
    print(section("Step 4 · Accounts & Opening Balances"))
    balances = load_balances()
    cfg["accounts"] = []

    if prompt_yes_no("Set up account names and opening balances?", default=True):
        print("  Common accounts: Octopus, HSBC, PayMe, Alipay HK, Cash")
        print("  Enter account names one per line. Leave blank to finish.\n")
        while True:
            acc = prompt(f"Account {len(cfg['accounts'])+1} name").strip()
            if not acc:
                break
            if acc in cfg["accounts"]:
                print("    ! Duplicate account.")
                continue
            cfg["accounts"].append(acc)
            bal = prompt_float(f"Opening balance for '{acc}' (HKD)", min_val=0.0, default=0.0)
            balances[acc] = bal

    if not cfg["accounts"]:
        cfg["accounts"] = ["Cash", "Bank"]
        balances.setdefault("Cash", 0.0)
        balances.setdefault("Bank", 0.0)
    save_balances(balances)

    # ── Finish ────────────────────────────────────────────────────────────────
    cfg["setup_complete"] = True
    save_config(cfg)
    print(f"\n  Setup complete! Welcome, {cfg['name']}.")
    print(f"  Your data is saved locally — everything stays on your machine.\n")
    pause()
    return cfg


def _prompt_period(category: str) -> str:
    print(f"  Period for '{category}':")
    print("    1. Daily")
    print("    2. Weekly")
    print("    3. Monthly  ← default (press Enter)")
    while True:
        raw = input("    Choose [1-3]: ").strip() or "3"
        if raw == "1":
            return "daily"
        if raw == "2":
            return "weekly"
        if raw == "3":
            return "monthly"
        print("    ! Enter 1, 2, or 3.")


# ── Post-setup helpers ────────────────────────────────────────────────────────

def update_categories(cfg: dict) -> dict:
    """Allow user to add/remove categories interactively."""
    print(header("Manage Categories"))
    cats = list(cfg.get("categories", []))
    wants = set(cfg.get("want_categories", []))
    needs = set(cfg.get("need_categories", []))

    while True:
        print("\n  Current categories:")
        for i, c in enumerate(cats, 1):
            tag = "want" if c in wants else "need"
            print(f"    {i}. {c} [{tag}]")
        print("\n  Options:")
        print("    a) Add category")
        print("    r) Remove category")
        print("    d) Done")
        choice = input("  > ").strip().lower()

        if choice == "a":
            name = prompt_required("New category name")
            if name in cats:
                print("    ! Already exists.")
            else:
                cats.append(name)
                t = prompt("  Type (want/need)", default="want").lower()
                if t in ("need", "n"):
                    needs.add(name)
                else:
                    wants.add(name)
        elif choice == "r":
            idx = prompt_int("Remove category number", 1, len(cats)) - 1
            removed = cats.pop(idx)
            wants.discard(removed)
            needs.discard(removed)
            print(f"    Removed '{removed}'.")
        elif choice == "d":
            break

    cfg["categories"] = cats
    cfg["want_categories"] = list(wants)
    cfg["need_categories"] = list(needs)
    save_config(cfg)
    return cfg


def update_credit_categories(cfg: dict) -> dict:
    """Allow user to add/remove income (credit) categories interactively."""
    print(header("Manage Income Categories"))
    cats = list(cfg.get("credit_categories", list(DEFAULT_CREDIT_CATEGORIES)))

    while True:
        print("\n  Current income categories:")
        for i, c in enumerate(cats, 1):
            print(f"    {i}. {c}")
        print("\n  Options:")
        print("    a) Add category")
        print("    r) Remove category")
        print("    d) Done")
        choice = input("  > ").strip().lower()

        if choice == "a":
            name = prompt_required("New income category name")
            if name in cats:
                print("    ! Already exists.")
            else:
                cats.append(name)
        elif choice == "r":
            idx = prompt_int("Remove category number", 1, len(cats)) - 1
            removed = cats.pop(idx)
            print(f"    Removed '{removed}'.")
        elif choice == "d":
            break

    cfg["credit_categories"] = cats
    save_config(cfg)
    return cfg


