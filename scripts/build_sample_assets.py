from __future__ import annotations

from pathlib import Path
import sys
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.finance_pipeline import run_pipeline

RAW_SAMPLE_PATH = ROOT / "data" / "sample" / "raw_transactions_sample.csv"
CLEAN_SAMPLE_PATH = ROOT / "data" / "sample" / "cleaned_transactions_sample.csv"
RULES_PATH = ROOT / "data" / "reference" / "classification_rules.csv"
QUALITY_DIR = ROOT / "data" / "quality"
IMAGES_DIR = ROOT / "images"

SAMPLE_SEED = 11
rng = random.Random(SAMPLE_SEED)

CANONICAL_DETAILS = {
    "food": {
        "Harbor Mart": ("groceries", [120, 340, 580, 920]),
        "Northside Grocer": ("groceries", [180, 360, 640, 980]),
        "Fresh Basket": ("groceries", [95, 210, 420, 760]),
        "Luna Cafe": ("restaurants", [140, 220, 320]),
        "Comet Burgers": ("restaurants", [180, 260, 390]),
        "Pier Pizza": ("restaurants", [250, 410, 620]),
        "Daily Roaster": ("snacks_drinks", [80, 120, 160]),
        "Spark Soda": ("snacks_drinks", [55, 85, 110]),
    },
    "other_things": {
        "Nova Books": ("shopping", [260, 420, 780]),
        "Metro Home": ("shopping", [450, 780, 1350]),
        "Orbit Pharmacy": ("healthcare", [210, 420, 960]),
        "Pixel Hub": ("home_office", [890, 1450, 2600]),
        "Trail Outfitters": ("shopping", [640, 980, 1820]),
        "Gift Loft": ("family_support", [300, 520, 940]),
    },
    "subscriptions": {
        "Streamly": ("subscriptions", [249, 349]),
        "CloudBox": ("subscriptions", [199, 299]),
        "Fit Circle": ("subscriptions", [550, 650]),
        "Music Now": ("subscriptions", [120, 160]),
    },
    "family": {
        "School Lunch": ("family_support", [180, 320, 480]),
        "Family Medicine": ("healthcare", [340, 620, 880]),
        "Family Gift": ("family_support", [220, 450, 750]),
        "House Allowance": ("family_support", [500, 900, 1200]),
    },
    "income": {
        "Monthly Payroll": ("salary", [22000, 23000, 24000]),
        "Consulting Client": ("freelance", [3800, 5200, 7600]),
        "Project Bonus": ("other_income", [1200, 1800]),
        "Cashback Reward": ("other_income", [120, 220]),
    },
}

DETAIL_VARIANTS = {
    "Harbor Mart": ["Harbor Mart", " harbor mart ", "HARBOR MART", "Harbor  Mart", "Harbor-Mart"],
    "Northside Grocer": ["Northside Grocer", "northside grocer", "Northside  Grocer", "NORTHSIDE GROCER"],
    "Fresh Basket": ["Fresh Basket", "fresh basket", "Fresh  Basket", "FRESH BASKET"],
    "Luna Cafe": ["Luna Cafe", "luna cafe ", "LUNA CAFE", "Luna  Cafe"],
    "Comet Burgers": ["Comet Burgers", "comet burgers", "COMET BURGERS", "Comet-Burgers"],
    "Pier Pizza": ["Pier Pizza", "pier pizza", "PIER PIZZA"],
    "Daily Roaster": ["Daily Roaster", "daily roaster", "Daily  Roaster"],
    "Spark Soda": ["Spark Soda", "spark soda", "SPARK SODA", "Spark  Soda"],
    "Nova Books": ["Nova Books", "nova books", "NOVA BOOKS", "Nova  Books"],
    "Metro Home": ["Metro Home", "metro home", "METRO HOME", "Metro-Home"],
    "Orbit Pharmacy": ["Orbit Pharmacy", "orbit pharmacy", "ORBIT PHARMACY"],
    "Pixel Hub": ["Pixel Hub", "pixel hub", "PIXEL HUB", "Pixel  Hub"],
    "Trail Outfitters": ["Trail Outfitters", "trail outfitters", "TRAIL OUTFITTERS"],
    "Gift Loft": ["Gift Loft", "gift loft", "GIFT LOFT"],
    "Streamly": ["Streamly", "streamly", "STREAMLY"],
    "CloudBox": ["CloudBox", "cloudbox", "Cloud Box", "CLOUDBOX"],
    "Fit Circle": ["Fit Circle", "fit circle", "FIT CIRCLE"],
    "Music Now": ["Music Now", "music now", "MUSIC NOW"],
    "School Lunch": ["School Lunch", "school lunch", "SCHOOL LUNCH"],
    "Family Medicine": ["Family Medicine", "family medicine", "FAMILY MEDICINE"],
    "Family Gift": ["Family Gift", "family gift", "FAMILY GIFT"],
    "House Allowance": ["House Allowance", "house allowance", "HOUSE ALLOWANCE"],
    "Monthly Payroll": ["Monthly Payroll", "monthly payroll", "MONTHLY PAYROLL", "Payroll - Main"],
    "Consulting Client": ["Consulting Client", "consulting client", "CONSULTING CLIENT", "Client Project Fee"],
    "Project Bonus": ["Project Bonus", "project bonus", "PROJECT BONUS"],
    "Cashback Reward": ["Cashback Reward", "cashback reward", "CASHBACK REWARD"],
}

UNMAPPED_DETAILS = [
    "Corner Cart",
    "Mango Shake Kiosk",
    "Weekend Trip",
]

RULE_ROWS = [
    ("food", "harbor_mart", "groceries", "", "", "", "fictional_public_rule"),
    ("food", "northside_grocer", "groceries", "", "", "", "fictional_public_rule"),
    ("food", "fresh_basket", "groceries", "", "", "", "fictional_public_rule"),
    ("food", "luna_cafe", "restaurants", "", "", "", "fictional_public_rule"),
    ("food", "comet_burgers", "restaurants", "", "", "", "fictional_public_rule"),
    ("food", "pier_pizza", "restaurants", "", "", "", "fictional_public_rule"),
    ("food", "daily_roaster", "snacks_drinks", "", "", "", "fictional_public_rule"),
    ("food", "spark_soda", "snacks_drinks", "", "", "", "fictional_public_rule"),
    ("other_things", "nova_books", "shopping", "books", "capital", "one_off", "fictional_public_rule"),
    ("other_things", "metro_home", "shopping", "household", "capital", "one_off", "fictional_public_rule"),
    ("other_things", "orbit_pharmacy", "healthcare", "", "operating", "one_off", "fictional_public_rule"),
    ("other_things", "pixel_hub", "home_office", "electronics", "capital", "one_off", "fictional_public_rule"),
    ("other_things", "trail_outfitters", "shopping", "travel", "capital", "one_off", "fictional_public_rule"),
    ("other_things", "gift_loft", "family_support", "", "operating", "one_off", "fictional_public_rule"),
    ("subscriptions", "streamly", "subscriptions", "", "operating", "recurring", "fictional_public_rule"),
    ("subscriptions", "cloudbox", "subscriptions", "", "operating", "recurring", "fictional_public_rule"),
    ("subscriptions", "fit_circle", "subscriptions", "", "operating", "recurring", "fictional_public_rule"),
    ("subscriptions", "music_now", "subscriptions", "", "operating", "recurring", "fictional_public_rule"),
    ("family", "school_lunch", "family_support", "", "operating", "recurring", "fictional_public_rule"),
    ("family", "family_medicine", "healthcare", "", "operating", "one_off", "fictional_public_rule"),
    ("family", "family_gift", "family_support", "", "operating", "one_off", "fictional_public_rule"),
    ("family", "house_allowance", "family_support", "", "operating", "recurring", "fictional_public_rule"),
    ("income", "monthly_payroll", "salary", "", "income", "recurring", "fictional_public_rule"),
    ("income", "consulting_client", "freelance", "", "income", "one_off", "fictional_public_rule"),
    ("income", "project_bonus", "other_income", "", "income", "one_off", "fictional_public_rule"),
    ("income", "cashback_reward", "other_income", "", "income", "one_off", "fictional_public_rule"),
]

UTILITY_AMOUNTS = [
    3200, 3400, 3500, 3650, 3800, 4100, 4200, 4500,
]
TRANSPORT_AMOUNTS = [45, 80, 120, 160, 240, 340]


def ensure_dirs() -> None:
    for directory in [RAW_SAMPLE_PATH.parent, CLEAN_SAMPLE_PATH.parent, RULES_PATH.parent, QUALITY_DIR, IMAGES_DIR]:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            raise RuntimeError(f"Failed to create directory: {directory}") from exc


def write_csv(df: pd.DataFrame, path: Path, *, header: bool = True) -> None:
    try:
        df.to_csv(path, index=False, header=header)
    except Exception as exc:
        raise RuntimeError(f"Failed to write CSV: {path}") from exc


def save_figure(fig: plt.Figure, path: Path, **kwargs) -> None:
    try:
        fig.savefig(path, **kwargs)
    except Exception as exc:
        raise RuntimeError(f"Failed to write image: {path}") from exc


def write_rules() -> None:
    rules = pd.DataFrame(
        RULE_ROWS,
        columns=[
            "category_scope",
            "detail_clean",
            "detail_grouped",
            "shopping_type",
            "expense_type_override",
            "recurrence_override",
            "note",
        ],
    )
    write_csv(rules, RULES_PATH)


def varied_detail(canonical: str) -> str | None:
    if rng.random() < 0.06:
        return None
    return rng.choice(DETAIL_VARIANTS[canonical])


def varied_amount(value: int | float) -> object:
    if rng.random() < 0.12:
        return f" {value:,} "
    return value


def pick_detail(category: str) -> tuple[str | None, float]:
    if rng.random() < 0.08 and category != "income":
        detail = rng.choice(UNMAPPED_DETAILS)
        amount = rng.choice([120, 240, 360, 540, 880])
        return detail, float(amount)

    canonical = rng.choice(list(CANONICAL_DETAILS[category]))
    _, amounts = CANONICAL_DETAILS[category][canonical]
    amount = float(rng.choice(amounts))
    return varied_detail(canonical), amount


def make_source_rows() -> list[list[object]]:
    rows = []
    rows.append(["", "Food", "", "Other Things", "", "Subscriptions", "", "Housing / Utilities", "Transport", "Notes", "Family", "", "Account Ref", "Income", ""]) 
    rows.append(["", "", "", "", "", "", "", "", "", "Demo Export", "", "", "", "", ""]) 
    rows.append(["Total", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]) 
    rows.append(["", "", "", "", "", "", "", "", "", "Generated for portfolio only", "", "", "", "", ""]) 
    rows.append(["", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]) 

    dates = pd.date_range("2024-01-03", "2024-06-28", freq="D")
    active_dates = [date for date in dates if date.weekday() < 5]
    income_dates = [date for date in active_dates if date.day in {1, 15}]
    other_dates = [date for date in active_dates if date not in income_dates]
    chosen_dates = sorted(income_dates + rng.sample(other_dates, 102))

    previous_date = None
    for date in chosen_dates:
        row = ["" for _ in range(15)]
        row[0] = date.strftime("%Y-%m-%d")

        food_detail, food_amount = pick_detail("food")
        row[1] = varied_amount(food_amount)
        row[2] = food_detail

        if rng.random() < 0.34:
            other_detail, other_amount = pick_detail("other_things")
            row[3] = varied_amount(other_amount)
            row[4] = other_detail

        if rng.random() < 0.11:
            sub_detail, sub_amount = pick_detail("subscriptions")
            row[5] = varied_amount(sub_amount)
            row[6] = sub_detail

        if rng.random() < 0.10:
            row[7] = varied_amount(rng.choice(UTILITY_AMOUNTS))

        if rng.random() < 0.44:
            row[8] = varied_amount(rng.choice(TRANSPORT_AMOUNTS))

        if rng.random() < 0.13:
            family_detail, family_amount = pick_detail("family")
            row[10] = varied_amount(family_amount)
            row[11] = family_detail

        if date.day == 1:
            row[13] = varied_amount(float(rng.choice([22000, 23000, 24000])))
            row[14] = rng.choice(DETAIL_VARIANTS["Monthly Payroll"])
        elif date.day == 15:
            if rng.random() < 0.7:
                row[13] = varied_amount(float(rng.choice([22000, 23000, 24000])))
                row[14] = rng.choice(DETAIL_VARIANTS["Monthly Payroll"])
            else:
                income_detail, income_amount = pick_detail("income")
                row[13] = varied_amount(income_amount)
                row[14] = income_detail

        if rng.random() < 0.18 and previous_date is not None:
            continuation = ["" for _ in range(15)]
            continuation_food, continuation_food_amount = pick_detail("food")
            continuation[1] = varied_amount(continuation_food_amount)
            continuation[2] = continuation_food
            if rng.random() < 0.35:
                continuation[3] = varied_amount(rng.choice([220, 390, 610, 940]))
                continuation[4] = rng.choice(["Corner Cart", "Weekend Trip", "Mango Shake Kiosk", "gift loft "])
            rows.append(row)
            rows.append(continuation)
        else:
            rows.append(row)

        previous_date = date

    return rows


def write_raw_sample() -> None:
    raw = pd.DataFrame(make_source_rows())
    write_csv(raw, RAW_SAMPLE_PATH, header=False)


def build_workflow_image() -> None:
    fig, ax = plt.subplots(figsize=(12, 3.8))
    ax.axis("off")
    steps = [
        (0.08, "Messy sample\nCSV export"),
        (0.30, "Wide-to-tidy\nreshape"),
        (0.52, "Rule-based\nclassification"),
        (0.74, "Quality checks\n+ review file"),
        (0.92, "Analysis-ready\nclean dataset"),
    ]
    for x, label in steps:
        ax.text(
            x,
            0.5,
            label,
            ha="center",
            va="center",
            fontsize=13,
            bbox={"boxstyle": "round,pad=0.6", "facecolor": "#f5f7fb", "edgecolor": "#24415c", "linewidth": 1.5},
            transform=ax.transAxes,
        )
    for start, end in zip(steps[:-1], steps[1:]):
        ax.annotate("", xy=(end[0] - 0.07, 0.5), xytext=(start[0] + 0.07, 0.5), xycoords=ax.transAxes, arrowprops={"arrowstyle": "->", "lw": 2, "color": "#24415c"})
    fig.tight_layout()
    save_figure(fig, IMAGES_DIR / "workflow.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def build_dashboard_images(cleaned: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")
    monthly = (
        cleaned.groupby(["year_month", "transaction_direction"], as_index=False)["amount"].sum()
        .pivot(index="year_month", columns="transaction_direction", values="amount")
        .fillna(0)
        .reset_index()
    )
    for required_column in ["income", "expense"]:
        if required_column not in monthly.columns:
            monthly[required_column] = 0.0
    monthly["savings_rate"] = np.where(
        monthly["income"] > 0,
        (monthly["income"] - monthly["expense"]) / monthly["income"],
        0,
    )

    expense_only = cleaned.loc[cleaned["transaction_direction"].eq("expense")].copy()
    category_spend = expense_only.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    top_merchants = (
        expense_only.loc[expense_only["detail_grouped"].ne("needs_review")]
        .groupby("detail_grouped", as_index=False)["amount"].sum()
        .sort_values("amount", ascending=False)
        .head(8)
    )

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(monthly["year_month"], monthly["income"], marker="o", label="Income", linewidth=2.5)
    ax.plot(monthly["year_month"], monthly["expense"], marker="o", label="Expenses", linewidth=2.5)
    ax.set_title("Monthly Income vs Expenses")
    ax.set_xlabel("")
    ax.set_ylabel("Amount")
    ax.legend()
    fig.autofmt_xdate(rotation=40)
    fig.tight_layout()
    save_figure(fig, IMAGES_DIR / "dashboard_monthly.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    sns.barplot(data=category_spend, x="amount", y="category", color="#4c78a8", ax=ax)
    ax.set_title("Spending by Category")
    ax.set_xlabel("Amount")
    ax.set_ylabel("")
    fig.tight_layout()
    save_figure(fig, IMAGES_DIR / "dashboard_categories.png", dpi=180)
    plt.close(fig)

    fig = plt.figure(figsize=(14, 9))
    grid = fig.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[1.15, 1])

    ax1 = fig.add_subplot(grid[0, 0])
    ax1.plot(monthly["year_month"], monthly["income"], marker="o", label="Income", linewidth=2.2)
    ax1.plot(monthly["year_month"], monthly["expense"], marker="o", label="Expenses", linewidth=2.2)
    ax1.set_title("Monthly Spending")
    ax1.tick_params(axis="x", rotation=35)
    ax1.legend(frameon=False)

    ax2 = fig.add_subplot(grid[0, 1])
    sns.barplot(data=category_spend, x="amount", y="category", color="#72b7b2", ax=ax2)
    ax2.set_title("Spending by Category")
    ax2.set_xlabel("Amount")
    ax2.set_ylabel("")

    ax3 = fig.add_subplot(grid[1, 0])
    sns.barplot(data=top_merchants, x="amount", y="detail_grouped", color="#f58518", ax=ax3)
    ax3.set_title("Top Merchants / Groups")
    ax3.set_xlabel("Amount")
    ax3.set_ylabel("")

    ax4 = fig.add_subplot(grid[1, 1])
    ax4.bar(monthly["year_month"], monthly["savings_rate"] * 100, color="#2b8cbe")
    ax4.axhline(0, color="#444", linewidth=1)
    ax4.set_title("Savings Rate")
    ax4.set_ylabel("Percent")
    ax4.tick_params(axis="x", rotation=35)

    fig.suptitle("Personal Finance Tracking Demo Dashboard", fontsize=18, y=0.98)
    fig.tight_layout()
    save_figure(fig, IMAGES_DIR / "dashboard_overview.png", dpi=180)
    plt.close(fig)


def main() -> None:
    global rng
    rng = random.Random(SAMPLE_SEED)
    ensure_dirs()
    write_rules()
    write_raw_sample()
    artifacts = run_pipeline(
        input_path=RAW_SAMPLE_PATH,
        rules_path=RULES_PATH,
        clean_output_path=CLEAN_SAMPLE_PATH,
        summary_output_path=QUALITY_DIR / "cleaning_summary_sample.csv",
        unmapped_output_path=QUALITY_DIR / "unmapped_details_sample.csv",
    )
    build_workflow_image()
    build_dashboard_images(artifacts.cleaned)
    print(f"Wrote raw sample: {RAW_SAMPLE_PATH}")
    print(f"Wrote cleaned sample: {CLEAN_SAMPLE_PATH}")
    print(f"Rows: {len(artifacts.cleaned):,}")
    print(f"Needs review rows: {artifacts.summary.loc[0, 'needs_review_rows']}")


if __name__ == "__main__":
    main()
