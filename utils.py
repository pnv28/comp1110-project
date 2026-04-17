"""Shared helpers: input validation, formatting, prompts."""

from datetime import datetime, date
import os

HKD_SYMBOL = "HKD"
DATE_FMT = "%Y-%m-%d"

# ── Formatting ────────────────────────────────────────────────────────────────

def fmt_amount(amount: float) -> str:
    return f"HKD {amount:,.2f}"


def fmt_date(d: date) -> str:
    return d.strftime(DATE_FMT)


def divider(char: str = "─", width: int = 60) -> str:
    return char * width


def header(title: str, width: int = 60) -> str:
    bar = divider("═", width)
    return f"\n{bar}\n  {title}\n{bar}"


def section(title: str, width: int = 60) -> str:
    return f"\n{divider('─', width)}\n  {title}\n{divider('─', width)}"


# ── Input helpers ─────────────────────────────────────────────────────────────

def prompt(msg: str, default: str = "") -> str:
    """Simple prompt; returns stripped input."""
    suffix = f" [{default}]" if default else ""
    raw = input(f"  {msg}{suffix}: ").strip()
    return raw if raw else default


def prompt_required(msg: str) -> str:
    """Keep asking until the user provides a non-empty value."""
    while True:
        val = prompt(msg)
        if val:
            return val
        print("    ! This field is required.")


def prompt_int(msg: str, min_val: int = 1, max_val: int = 9999,
               default: int | None = None) -> int:
    default_str = str(default) if default is not None else ""
    while True:
        raw = prompt(msg, default_str)
        try:
            val = int(raw)
            if min_val <= val <= max_val:
                return val
            print(f"    ! Enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("    ! Please enter a valid integer.")


def prompt_float(msg: str, min_val: float = 0.01,
                 default: float | None = None) -> float:
    default_str = f"{default:.2f}" if default is not None else ""
    while True:
        raw = prompt(msg, default_str)
        try:
            val = float(raw)
            if val >= min_val:
                return round(val, 2)
            print(f"    ! Amount must be at least {min_val:.2f}.")
        except ValueError:
            print("    ! Please enter a valid number (e.g. 45.50).")


def prompt_date(msg: str, default: str = "") -> date:
    """Prompt for a date in YYYY-MM-DD format."""
    if not default:
        default = date.today().strftime(DATE_FMT)
    while True:
        raw = prompt(msg, default)
        try:
            return datetime.strptime(raw, DATE_FMT).date()
        except ValueError:
            print(f"    ! Enter date as YYYY-MM-DD (e.g. {date.today().strftime(DATE_FMT)}).")


DEFAULT_HINT = (
    "  Tip: Values in [brackets] are defaults — press Enter to accept.\n"
    "       In Y/n prompts the CAPITAL letter is the default (e.g. Y/n → Enter = Yes)."
)


def prompt_choice(msg: str, options: list[str],
                  default: str = "", allow_new: bool = False) -> str:
    """Present numbered options; return chosen string."""
    print(f"  {msg}")
    if default in options:
        print(f"  (Press Enter to select the default marked with ←)")
    for i, opt in enumerate(options, 1):
        marker = " ← default" if opt == default else ""
        print(f"    {i}. {opt}{marker}")
    if allow_new:
        print(f"    {len(options)+1}. [Enter new value]")

    while True:
        raw = prompt("Choose number", str(options.index(default) + 1) if default in options else "").strip()
        if not raw and default:
            return default
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx]
            if allow_new and idx == len(options):
                return prompt_required("Enter new value")
            print(f"    ! Enter 1–{len(options) + (1 if allow_new else 0)}.")
        except ValueError:
            # User typed the value directly
            if raw in options:
                return raw
            if allow_new:
                return raw
            print("    ! Please enter a number from the list.")


def prompt_yes_no(msg: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    while True:
        raw = prompt(f"{msg} ({hint})").lower()
        if not raw:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("    ! Please enter y or n.")


def prompt_period(msg: str = "Period", default: str = "monthly") -> str:
    return prompt_choice(msg, ["daily", "weekly", "monthly"], default=default)


# ── Validation ────────────────────────────────────────────────────────────────

def validate_date_str(s: str) -> bool:
    try:
        datetime.strptime(s, DATE_FMT)
        return True
    except ValueError:
        return False


def validate_amount(s: str) -> bool:
    try:
        return float(s) > 0
    except ValueError:
        return False


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    input("\n  Press Enter to continue...")
