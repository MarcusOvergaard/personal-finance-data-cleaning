from __future__ import annotations

from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path
import re

import numpy as np
import pandas as pd

FIRST_DATA_ROW = 6
SOURCE_SHEET_NAME = "SampleExport"
EXPECTED_RULE_COLUMNS = [
    "category_scope",
    "detail_clean",
    "detail_grouped",
    "shopping_type",
    "expense_type_override",
    "recurrence_override",
    "note",
]
FINAL_COLUMNS = [
    "date",
    "year",
    "month",
    "month_name",
    "year_month",
    "category",
    "transaction_direction",
    "amount",
    "signed_amount",
    "detail_raw",
    "detail_clean",
    "detail_grouped",
    "classification_source",
    "shopping_type",
    "expense_type",
    "recurrence",
    "source_file",
    "source_sheet",
    "source_row",
]


@dataclass(frozen=True)
class PipelineArtifacts:
    raw: pd.DataFrame
    transaction_area: pd.DataFrame
    tidy: pd.DataFrame
    cleaned: pd.DataFrame
    rules: pd.DataFrame
    summary: pd.DataFrame
    unmapped: pd.DataFrame


KEYWORD_RULES = [
    (r"salary|payroll|pay_day|monthly_pay", "salary"),
    (r"freelance|consulting|project_fee|client", "freelance"),
    (r"bonus|cashback|refund", "other_income"),
    (r"harbor|grocer|market|fresh|farm|basket", "groceries"),
    (r"cafe|coffee|roaster|burger|bistro|pizza|ramen|diner", "restaurants"),
    (r"stream|cloudbox|music|gym|storage|member", "subscriptions"),
    (r"metro|ride|fuel|bus|taxi|garage", "transport"),
    (r"power|water|rent|internet|utility", "housing_utilities"),
    (r"pharma|clinic|med|dental", "healthcare"),
    (r"book|home|desk|lamp|luggage|cable|device|shop", "shopping"),
    (r"gift|family|school|allowance", "family_support"),
]


DEFAULT_EXPENSE_TYPE_BY_GROUP = {
    "groceries": "operating",
    "restaurants": "operating",
    "snacks_drinks": "operating",
    "subscriptions": "operating",
    "transport": "operating",
    "housing_utilities": "operating",
    "healthcare": "operating",
    "family_support": "operating",
    "shopping": "capital",
    "home_office": "capital",
    "travel": "one_off",
    "other_income": "income",
    "salary": "income",
    "freelance": "income",
}

DEFAULT_RECURRENCE_BY_GROUP = {
    "salary": "recurring",
    "freelance": "one_off",
    "other_income": "one_off",
    "groceries": "recurring",
    "restaurants": "recurring",
    "snacks_drinks": "recurring",
    "subscriptions": "recurring",
    "transport": "recurring",
    "housing_utilities": "recurring",
    "healthcare": "one_off",
    "family_support": "one_off",
    "shopping": "one_off",
    "home_office": "one_off",
    "travel": "one_off",
}


COLUMN_MAP = {
    0: "date",
    1: "food",
    2: "food_detail",
    3: "other_things",
    4: "other_things_detail",
    5: "subscriptions",
    6: "subscriptions_detail",
    7: "housing_utilities",
    8: "transport",
    10: "family",
    11: "family_detail",
    13: "income",
    14: "income_detail",
    "source_row": "source_row",
}
DETAILED_CATEGORIES = {
    "food": "food_detail",
    "other_things": "other_things_detail",
    "subscriptions": "subscriptions_detail",
    "family": "family_detail",
    "income": "income_detail",
}
SIMPLE_CATEGORIES = ["housing_utilities", "transport"]


def ensure_parent_dir(path: str | Path) -> Path:
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        raise RuntimeError(f"Failed to create output directory for: {path}") from exc
    return path


def load_raw_table(input_path: str | Path) -> pd.DataFrame:
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    suffix = input_path.suffix.lower()
    try:
        if suffix in {".xlsx", ".xlsm"}:
            raw = pd.read_excel(input_path, sheet_name=0, header=None, engine="openpyxl")
        else:
            raw = pd.read_csv(input_path, header=None)
    except Exception as exc:
        raise RuntimeError(f"Failed to read input file: {input_path}") from exc
    raw["source_row"] = raw.index + 1
    return raw


def prepare_transaction_area(raw: pd.DataFrame, first_data_row: int = FIRST_DATA_ROW) -> pd.DataFrame:
    data = raw.loc[raw["source_row"] >= first_data_row, list(COLUMN_MAP.keys())].rename(columns=COLUMN_MAP).copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["date"] = data["date"].ffill()
    return data


def reshape_transactions(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for amount_col, detail_col in DETAILED_CATEGORIES.items():
        temp = data[["date", amount_col, detail_col, "source_row"]].copy()
        temp = temp.rename(columns={amount_col: "amount", detail_col: "detail_raw"})
        temp["category"] = amount_col
        rows.append(temp)

    for amount_col in SIMPLE_CATEGORIES:
        temp = data[["date", amount_col, "source_row"]].copy()
        temp = temp.rename(columns={amount_col: "amount"})
        temp["detail_raw"] = pd.NA
        temp["category"] = amount_col
        rows.append(temp)

    tidy = pd.concat(rows, ignore_index=True)
    tidy["amount"] = clean_amount_series(tidy["amount"])
    tidy["detail_raw"] = tidy["detail_raw"].replace(r"^\s*$", pd.NA, regex=True)
    tidy = tidy.dropna(subset=["amount"])
    tidy = tidy[tidy["amount"] > 0].copy()
    tidy["transaction_direction"] = np.where(tidy["category"].eq("income"), "income", "expense")
    tidy = tidy[["date", "category", "transaction_direction", "amount", "detail_raw", "source_row"]]
    return tidy


def clean_amount_series(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype("string")
        .str.replace(",", "", regex=False)
        .str.replace("₱", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace(r"\s+", "", regex=True)
    )
    cleaned = cleaned.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "<NA>": pd.NA})
    return pd.to_numeric(cleaned, errors="coerce")


def normalize_detail(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    value = str(value).strip().lower()
    value = value.replace("&", " and ")
    value = value.replace("/", " ")
    value = value.replace("-", " ")
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^a-z0-9_#]", "", value)
    value = re.sub(r"_+", "_", value)
    value = value.strip("_")
    return value or pd.NA


def load_rules(rules_path: str | Path) -> pd.DataFrame:
    rules_path = Path(rules_path)
    if not rules_path.exists():
        raise FileNotFoundError(f"Rules file not found: {rules_path}")
    try:
        rules = pd.read_csv(rules_path).fillna("")
    except Exception as exc:
        raise RuntimeError(f"Failed to read rules file: {rules_path}") from exc
    missing = [column for column in EXPECTED_RULE_COLUMNS if column not in rules.columns]
    if missing:
        raise ValueError(f"Rules file is missing columns: {missing}")
    rules["category_scope"] = rules["category_scope"].astype(str).str.strip().str.lower()
    rules["detail_clean"] = rules["detail_clean"].astype(str).str.strip().str.lower()
    return rules[EXPECTED_RULE_COLUMNS].copy()


def apply_rules(tidy: pd.DataFrame, rules: pd.DataFrame) -> pd.DataFrame:
    cleaned = tidy.copy()
    cleaned["detail_clean"] = cleaned["detail_raw"].apply(normalize_detail)
    cleaned["detail_grouped"] = pd.NA
    cleaned["classification_source"] = pd.NA
    cleaned["shopping_type"] = pd.NA
    cleaned["expense_type_override"] = pd.NA
    cleaned["recurrence_override"] = pd.NA

    specific_rules = {}
    global_rules = {}
    for row in rules.to_dict("records"):
        target = specific_rules if row["category_scope"] else global_rules
        key = (row["category_scope"], row["detail_clean"]) if row["category_scope"] else row["detail_clean"]
        target[key] = row

    for index, row in cleaned.loc[cleaned["detail_clean"].notna()].iterrows():
        detail_clean = row["detail_clean"]
        category = row["category"]
        rule = specific_rules.get((category, detail_clean)) or global_rules.get(detail_clean)
        if rule:
            cleaned.at[index, "detail_grouped"] = rule["detail_grouped"]
            cleaned.at[index, "classification_source"] = "exact_rule"
            cleaned.at[index, "shopping_type"] = rule["shopping_type"] or pd.NA
            cleaned.at[index, "expense_type_override"] = rule["expense_type_override"] or pd.NA
            cleaned.at[index, "recurrence_override"] = rule["recurrence_override"] or pd.NA

    keyword_mask = cleaned["detail_clean"].notna() & cleaned["detail_grouped"].isna()
    for pattern, grouped_name in KEYWORD_RULES:
        hits = keyword_mask & cleaned["detail_clean"].str.contains(pattern, case=False, regex=True)
        cleaned.loc[hits, "detail_grouped"] = grouped_name
        cleaned.loc[hits, "classification_source"] = "keyword_rule"
        keyword_mask = cleaned["detail_clean"].notna() & cleaned["detail_grouped"].isna()

    no_detail_mask = cleaned["detail_clean"].isna()
    cleaned.loc[no_detail_mask, "detail_grouped"] = cleaned.loc[no_detail_mask, "category"]
    cleaned.loc[no_detail_mask, "classification_source"] = "category_default_no_detail"

    review_mask = cleaned["detail_clean"].notna() & cleaned["detail_grouped"].isna()
    cleaned.loc[review_mask, "detail_grouped"] = "needs_review"
    cleaned.loc[review_mask, "classification_source"] = "needs_review"

    cleaned["expense_type"] = cleaned["detail_grouped"].map(DEFAULT_EXPENSE_TYPE_BY_GROUP).fillna("operating")
    cleaned["recurrence"] = cleaned["detail_grouped"].map(DEFAULT_RECURRENCE_BY_GROUP).fillna("recurring")

    income_mask = cleaned["transaction_direction"].eq("income")
    cleaned.loc[income_mask, "expense_type"] = "income"

    override_expense_mask = cleaned["expense_type_override"].notna()
    cleaned.loc[override_expense_mask, "expense_type"] = cleaned.loc[override_expense_mask, "expense_type_override"]

    override_recurrence_mask = cleaned["recurrence_override"].notna()
    cleaned.loc[override_recurrence_mask, "recurrence"] = cleaned.loc[override_recurrence_mask, "recurrence_override"]

    cleaned["signed_amount"] = np.where(
        cleaned["transaction_direction"].eq("income"),
        cleaned["amount"],
        -cleaned["amount"],
    )

    cleaned["year"] = cleaned["date"].dt.year
    cleaned["month"] = cleaned["date"].dt.month
    cleaned["month_name"] = cleaned["date"].dt.month_name()
    cleaned["year_month"] = cleaned["date"].dt.to_period("M").astype(str)

    cleaned = cleaned.drop(columns=["expense_type_override", "recurrence_override"])
    return cleaned


def finalize_dataset(cleaned: pd.DataFrame, input_path: str | Path, source_sheet_name: str = SOURCE_SHEET_NAME) -> pd.DataFrame:
    finalized = cleaned.copy()
    input_path = Path(input_path)
    finalized["source_file"] = input_path.name
    finalized["source_sheet"] = source_sheet_name
    return finalized[FINAL_COLUMNS].sort_values(["date", "source_row", "category", "amount"]).reset_index(drop=True)


def build_quality_outputs(cleaned: pd.DataFrame, rules: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rules_values = sorted(set(rules["detail_clean"].dropna().astype(str)))
    needs_review = cleaned.loc[cleaned["classification_source"].eq("needs_review")].copy()

    if needs_review.empty:
        unmapped = pd.DataFrame(
            columns=["category", "detail_clean", "count", "total_amount", "first_date", "last_date", "similar_existing_rule"]
        )
    else:
        unmapped = (
            needs_review.groupby(["category", "detail_clean"], dropna=False)
            .agg(
                count=("amount", "size"),
                total_amount=("amount", "sum"),
                first_date=("date", "min"),
                last_date=("date", "max"),
            )
            .reset_index()
            .sort_values(["total_amount", "count"], ascending=[False, False])
        )
        unmapped["first_date"] = unmapped["first_date"].dt.strftime("%Y-%m-%d")
        unmapped["last_date"] = unmapped["last_date"].dt.strftime("%Y-%m-%d")
        unmapped["similar_existing_rule"] = unmapped["detail_clean"].apply(
            lambda value: ", ".join(get_close_matches(str(value), rules_values, n=2, cutoff=0.72))
        )

    summary = pd.DataFrame(
        [
            {
                "rows": len(cleaned),
                "total_income": round(cleaned.loc[cleaned["transaction_direction"].eq("income"), "amount"].sum(), 2),
                "total_expenses": round(cleaned.loc[cleaned["transaction_direction"].eq("expense"), "amount"].sum(), 2),
                "net_cash_flow": round(cleaned["signed_amount"].sum(), 2),
                "start_date": cleaned["date"].min().strftime("%Y-%m-%d"),
                "end_date": cleaned["date"].max().strftime("%Y-%m-%d"),
                "missing_dates": int(cleaned["date"].isna().sum()),
                "missing_amounts": int(cleaned["amount"].isna().sum()),
                "needs_review_rows": int(cleaned["classification_source"].eq("needs_review").sum()),
                "needs_review_unique_details": int(needs_review["detail_clean"].nunique()),
            }
        ]
    )
    return summary, unmapped


def run_pipeline(
    input_path: str | Path,
    rules_path: str | Path,
    clean_output_path: str | Path | None = None,
    summary_output_path: str | Path | None = None,
    unmapped_output_path: str | Path | None = None,
) -> PipelineArtifacts:
    raw = load_raw_table(input_path)
    transaction_area = prepare_transaction_area(raw)
    tidy = reshape_transactions(transaction_area)
    rules = load_rules(rules_path)
    cleaned = apply_rules(tidy, rules)
    cleaned = finalize_dataset(cleaned, input_path)
    summary, unmapped = build_quality_outputs(cleaned, rules)

    if clean_output_path:
        clean_output_path = ensure_parent_dir(clean_output_path)
        try:
            cleaned.to_csv(clean_output_path, index=False)
        except Exception as exc:
            raise RuntimeError(f"Failed to write cleaned output: {clean_output_path}") from exc

    if summary_output_path:
        summary_output_path = ensure_parent_dir(summary_output_path)
        try:
            summary.to_csv(summary_output_path, index=False)
        except Exception as exc:
            raise RuntimeError(f"Failed to write summary output: {summary_output_path}") from exc

    if unmapped_output_path:
        unmapped_output_path = ensure_parent_dir(unmapped_output_path)
        try:
            unmapped.to_csv(unmapped_output_path, index=False)
        except Exception as exc:
            raise RuntimeError(f"Failed to write unmapped output: {unmapped_output_path}") from exc

    return PipelineArtifacts(
        raw=raw,
        transaction_area=transaction_area,
        tidy=tidy,
        cleaned=cleaned,
        rules=rules,
        summary=summary,
        unmapped=unmapped,
    )
