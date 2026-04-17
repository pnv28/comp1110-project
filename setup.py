"""First-run configuration flow."""

from data import load_config, save_config, save_rules, load_rules, save_balances, load_balances
from utils import (
    header, section, divider, prompt, prompt_required, prompt_float,
    prompt_yes_no, prompt_int, pause
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

DEFAULT_WANTS = {"Entertainment", "Shopping", "Social"}
DEFAULT_NEEDS = {"Food & Dining", "Transport", "Housing", "Health", "Education", "Utilities"}


def run_setup() -> dict:
    """Interactive first-run setup. Returns completed config dict."""
    print(header("Welcome to HK Student Budget Assistant"))
    print("""
  This one-time setup will personalise the app for you.
  You can change any of these settings later from the main menu.
""")

    cfg = load_config()

    # ── Step 1: User name ─────────────────────────────────────────────────────
    print(section("Step 1 of 5 · Your Profile"))
    cfg["name"] = prompt_required("Your name")
    cfg["university"] = prompt("University (e.g. HKU, CUHK, PolyU)")

    # ── Step 2: Monthly income / allowance ────────────────────────────────────
    print(section("Step 2 of 5 · Monthly Income / Allowance"))
    print("  Enter 0 if you prefer not to set this.")
    cfg["monthly_income"] = prompt_float("Monthly income or allowance (HKD)", min_val=0.0, default=0.0)

    # ── Step 3: Savings goal ──────────────────────────────────────────────────
    print(section("Step 3 of 5 · Savings Goal"))
    has_goal = prompt_yes_no("Do you have a monthly savings target?", default=True)
    if has_goal:
        cfg["savings_goal"] = prompt_float("Monthly savings goal (HKD)", min_val=1.0)
        cfg["savings_goal_name"] = prompt("What are you saving for?",
                                          default="Emergency fund")
    else:
        cfg["savings_goal"] = 0.0
        cfg["savings_goal_name"] = ""

    # ── Step 4: Spending categories ───────────────────────────────────────────
    print(section("Step 4 of 5 · Spending Categories"))
    print("  Default categories:")
    for cat in DEFAULT_CATEGORIES:
        print(f"    • {cat}")

    use_defaults = prompt_yes_no("Use these default categories?", default=True)
    if use_defaults:
        categories = list(DEFAULT_CATEGORIES)
    else:
        categories = []
        print("  Enter categories one per line. Leave blank to finish.")
        print("  (You must enter at least 3)")
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

    cfg["categories"] = categories

    # ── Step 4b: Want/Need classification ─────────────────────────────────────
    print("\n  Classify each category as 'want' or 'need':")
    print("  (This is used for auto-classification; you can always override.)\n")
    want_set = set()
    need_set = set()
    for cat in categories:
        if cat in DEFAULT_WANTS:
            suggestion = "want"
        elif cat in DEFAULT_NEEDS:
            suggestion = "need"
        else:
            suggestion = "want"
        choice = prompt(f"  '{cat}' — want or need?", default=suggestion).lower().strip()
        while choice not in ("want", "need", "w", "n"):
            choice = prompt(f"  '{cat}' — want or need?", default=suggestion).lower().strip()
        if choice in ("want", "w"):
            want_set.add(cat)
        else:
            need_set.add(cat)

    cfg["want_categories"] = list(want_set)
    cfg["need_categories"] = list(need_set)

    # ── Step 5: Budget rules ──────────────────────────────────────────────────
    print(section("Step 5 of 5 · Budget Limits (optional)"))
    print("  Set spending limits per category. Press Enter to skip a category.\n")

    rules = load_rules()
    existing_cats = {r["category"] for r in rules}

    for cat in categories:
        skip = not prompt_yes_no(f"Set a budget limit for '{cat}'?", default=False)
        if skip:
            continue
        limit = prompt_float(f"  Limit for '{cat}' (HKD)")
        period = _prompt_period(f"  Period for '{cat}'")
        # Remove existing rule for category if present
        rules = [r for r in rules if r["category"] != cat]
        rules.append({"category": cat, "limit_amount": limit, "period": period})

    save_rules(rules)

    # ── Accounts / opening balances ───────────────────────────────────────────
    print(section("Accounts & Opening Balances (optional)"))
    add_accounts = prompt_yes_no("Set up account names and opening balances?", default=True)
    balances = load_balances()
    cfg["accounts"] = []

    if add_accounts:
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
            bal = prompt_float(f"  Opening balance for '{acc}' (HKD)", min_val=0.0, default=0.0)
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


def _prompt_period(msg: str) -> str:
    print(f"  {msg}")
    print("    1. Daily")
    print("    2. Weekly")
    print("    3. Monthly")
    while True:
        raw = input("    Choose [1-3] (default 3): ").strip() or "3"
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


def update_savings_goal(cfg: dict) -> dict:
    print(header("Update Savings Goal"))
    cfg["savings_goal"] = prompt_float("Monthly savings goal (HKD, 0 to disable)",
                                       min_val=0.0, default=cfg.get("savings_goal", 0.0))
    if cfg["savings_goal"] > 0:
        cfg["savings_goal_name"] = prompt("What are you saving for?",
                                           default=cfg.get("savings_goal_name", ""))
    save_config(cfg)
    print("  Savings goal updated.")
    return cfg
