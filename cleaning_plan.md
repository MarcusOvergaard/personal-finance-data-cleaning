# Personal Finance Cleaning Plan

**Goal:** Turn `personal_finances_raw.xlsx` into a clean, Tableau-ready CSV, with a notebook that clearly shows every cleaning step.

**Raw source:** `/home/marcusai/MyProjects/PersonalFinanceTrackeing/personal_finances_raw.xlsx`

**Old notebook:** `/home/marcusai/MyProjects/PersonalFinanceTrackeing/PersonalFinances.ipynb`

**Recommended final output:** `data/cleaned/personal_finance_transactions_clean.csv`

---

## 1. Answer: Excel or CSV?

The Excel version is okay. You do **not** need to download it as CSV first.

Use the `.xlsx` file as the raw source because:

- it preserves the original workbook exactly;
- Python can read it directly with `pandas` + `openpyxl`;
- exporting manually to CSV can accidentally change dates, blank rows, encoding, or formulas;
- the notebook can produce the clean CSV automatically at the end.

The best workflow is:

`Excel raw file -> cleaning notebook -> clean CSV -> Tableau`

---

## 2. What I found in the current files

### Excel workbook

File: `personal_finances_raw.xlsx`

Observed structure:

- 1 sheet: `Sheet1`
- around 2,280 rows
- 28 columns
- real transaction table appears to start around row 6
- rows 1-3 contain headers/totals/summary information, not transaction data
- columns after roughly column L are mostly empty or summary junk

The useful columns appear to be:

| Excel column | Meaning |
|---|---|
| A | date |
| B | food amount |
| C | food detail |
| D | other things amount |
| E | other things detail |
| F | subscriptions amount |
| G | subscriptions detail |
| H | housing/utilities amount: `lege/strom/vand` |
| I | transport amount |
| J | hygge, mostly empty/unused |
| K | family amount |
| L | family detail |

Important pattern:

- A single Excel row can contain more than one transaction.
- Dates are often blank on continuation rows.
- The correct method is to forward-fill dates downward before reshaping the file.

### Existing notebook

File: `PersonalFinances.ipynb`

The notebook already contains useful logic:

- column name cleaning;
- dropping empty/junk columns;
- converting from wide format into tidy transaction rows;
- grouping details like restaurants, groceries, shopping, subscriptions, etc.;
- adding `expense_type` and `recurrence`;
- exporting to CSV.

But it is outdated because:

- it reads `PersonalFinancesUpdated.csv`, which is not currently in the folder;
- it relies on old column names from a CSV export rather than the current Excel workbook;
- it has hard-coded row fixes like `tidy.loc[2342, ...]`, which are fragile;
- the mappings are embedded inside notebook cells, making them harder to maintain;
- there are not enough validation checks before export.

---

## 3. Target data model

The cleaned CSV should be one transaction per row.

Recommended columns:

| Column | Meaning |
|---|---|
| `date` | transaction date |
| `year` | extracted from date |
| `month` | month number |
| `month_name` | readable month |
| `year_month` | Tableau-friendly period, e.g. `2025-03` |
| `category` | original major category: food, other_things, subscriptions, housing_utilities, transport, family |
| `amount` | numeric spending amount |
| `detail_raw` | original text from Excel |
| `detail_clean` | normalized detail, e.g. `SM Supermarket` -> `sm_supermarket` |
| `detail_grouped` | grouped label, e.g. `groceries`, `restaurants`, `shopping` |
| `shopping_type` | optional shopping subtype: books, clothing, gadgets, household, etc. |
| `expense_type` | operating, capital, construction |
| `recurrence` | recurring, one_off, construction |
| `source_file` | original filename |
| `source_sheet` | original sheet name |
| `source_row` | original Excel row number for auditing |

This is the right shape for Tableau because Tableau prefers long/tidy tables, not a wide Excel budget layout.

---

## 4. Proposed project structure

Create this structure:

```text
PersonalFinanceTrackeing/
  personal_finances_raw.xlsx                         # raw source, unchanged
  PersonalFinances.ipynb                   # old notebook, keep as reference
  01_clean_personal_finances.ipynb          # new cleaning notebook
  cleaning_plan.md                          # this plan
  data/
    cleaned/
      personal_finance_transactions_clean.csv
    quality/
      unmapped_details.csv
      cleaning_summary.csv
  src/
    finance_cleaning.py                     # optional helper functions if notebook gets too long
```

For now, the notebook can contain the cleaning code directly. If it becomes messy, move reusable functions into `src/finance_cleaning.py`.

---

## 5. Notebook plan

Create a new notebook instead of trying to patch the old one directly:

`01_clean_personal_finances.ipynb`

The old notebook should be used as a reference, not as the production cleaning workflow.

### Section 1: Setup

Install/use these packages:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas openpyxl matplotlib seaborn jupyter
```

Notebook imports:

```python
from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
```

Set paths:

```python
PROJECT_DIR = Path.cwd()
RAW_FILE = PROJECT_DIR / "personal_finances_raw.xlsx"
CLEAN_DIR = PROJECT_DIR / "data" / "cleaned"
QUALITY_DIR = PROJECT_DIR / "data" / "quality"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)
QUALITY_DIR.mkdir(parents=True, exist_ok=True)
```

### Section 2: Load the raw Excel file

Read without assuming headers:

```python
raw = pd.read_excel(
    RAW_FILE,
    sheet_name="Sheet1",
    header=None,
    engine="openpyxl"
)
```

Add an audit column for the Excel row number:

```python
raw["source_row"] = raw.index + 1
```

Display the first 15 rows so the notebook documents the messy source layout.

### Section 3: Remove summary/header rows and unused columns

Use the real data rows only. Based on inspection, transactions begin around Excel row 6.

```python
data = raw.loc[raw["source_row"] >= 6].copy()
```

Keep only the useful columns:

```python
cols = {
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
    "source_row": "source_row",
}

data = data[list(cols.keys())].rename(columns=cols)
```

Skip `hygge` for now because it appears mostly unused. If you want it later, add it explicitly as a real category.

### Section 4: Clean dates

Convert Excel dates to proper datetime values:

```python
data["date"] = pd.to_datetime(data["date"], errors="coerce")
data["date"] = data["date"].ffill()
```

Validation:

```python
assert data["date"].notna().all(), "Some rows still have missing dates after forward-fill"
```

### Section 5: Convert wide Excel layout into tidy transactions

The detailed amount/detail pairs are:

```python
detailed_categories = {
    "food": "food_detail",
    "other_things": "other_things_detail",
    "subscriptions": "subscriptions_detail",
    "family": "family_detail",
}
```

The simple amount-only categories are:

```python
simple_categories = ["housing_utilities", "transport"]
```

Build the tidy table:

```python
rows = []

for amount_col, detail_col in detailed_categories.items():
    temp = data[["date", amount_col, detail_col, "source_row"]].copy()
    temp = temp.rename(columns={amount_col: "amount", detail_col: "detail_raw"})
    temp["category"] = amount_col
    rows.append(temp)

for amount_col in simple_categories:
    temp = data[["date", amount_col, "source_row"]].copy()
    temp = temp.rename(columns={amount_col: "amount"})
    temp["detail_raw"] = pd.NA
    temp["category"] = amount_col
    rows.append(temp)

tidy = pd.concat(rows, ignore_index=True)
```

Clean the amount column:

```python
tidy["amount"] = pd.to_numeric(tidy["amount"], errors="coerce")
tidy = tidy.dropna(subset=["amount"])
tidy = tidy[tidy["amount"] > 0].copy()
```

### Section 6: Normalize detail names

Create a reusable text-cleaning function:

```python
def clean_detail(value):
    if pd.isna(value):
        return pd.NA
    value = str(value).strip().lower()
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^\wæøåÆØÅéÉüÜäÄöÖñÑ-]", "", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_")


tidy["detail_clean"] = tidy["detail_raw"].apply(clean_detail)
```

Keep both `detail_raw` and `detail_clean`. Do not overwrite the original text.

### Section 7: Apply category mapping

Reuse the old notebook mapping, but make it more maintainable.

Minimum first version:

```python
detail_group_mapping = {
    "mcdonalds": "restaurants",
    "sm_supermarket": "groceries",
    "nccc_supermarket": "groceries",
    "unitop": "shopping",
    "gym": "subscriptions",
    "piso_wifi": "mobile_data",
    # continue by copying/refining the old notebook mapping
}


tidy["detail_grouped"] = tidy["detail_clean"].map(detail_group_mapping)
```

For categories without details, default to the category:

```python
tidy["detail_grouped"] = tidy["detail_grouped"].fillna(tidy["category"])
```

Important: avoid hard-coded row fixes like this from the old notebook:

```python
tidy.loc[2342, "category"] = "food"
```

Instead, make explicit mapping rules. Example:

```python
# If Unitop is usually non-food shopping, map it to shopping.
detail_group_mapping["unitop"] = "shopping"
```

If a specific row truly needs correction, document it in a small correction table with `source_row`, old value, new value, and reason.

### Section 8: Add expense type and recurrence

Use explicit sets, not dictionaries with unused values.

```python
capital_details = {
    "phone", "tablet_ivy", "speaker", "shaver", "sd_kort_256gb",
    "shopee_router", "antenna", "kuffert"
}

one_off_details = capital_details | {
    "dentist_marcusivy", "dentist_ivy", "medical_expences",
    "visa_appointment", "insurance_shenguen"
}


tidy["expense_type"] = "operating"
tidy.loc[tidy["detail_clean"].isin(capital_details), "expense_type"] = "capital"
tidy.loc[tidy["detail_grouped"] == "construction", "expense_type"] = "construction"


tidy["recurrence"] = "recurring"
tidy.loc[tidy["detail_clean"].isin(one_off_details), "recurrence"] = "one_off"
tidy.loc[tidy["detail_grouped"] == "construction", "recurrence"] = "construction"
```

### Section 9: Add Tableau-friendly date columns

```python
tidy["year"] = tidy["date"].dt.year
tidy["month"] = tidy["date"].dt.month
tidy["month_name"] = tidy["date"].dt.month_name()
tidy["year_month"] = tidy["date"].dt.to_period("M").astype(str)
```

### Section 10: Add source metadata

```python
tidy["source_file"] = RAW_FILE.name
tidy["source_sheet"] = "Sheet1"
```

Final column order:

```python
final_columns = [
    "date", "year", "month", "month_name", "year_month",
    "category", "amount",
    "detail_raw", "detail_clean", "detail_grouped",
    "shopping_type", "expense_type", "recurrence",
    "source_file", "source_sheet", "source_row"
]

# Only include shopping_type if created.
existing_columns = [col for col in final_columns if col in tidy.columns]
tidy = tidy[existing_columns]
```

### Section 11: Data quality checks

Add checks before exporting:

```python
checks = {
    "rows": len(tidy),
    "total_amount": tidy["amount"].sum(),
    "missing_dates": tidy["date"].isna().sum(),
    "missing_amounts": tidy["amount"].isna().sum(),
    "negative_or_zero_amounts": (tidy["amount"] <= 0).sum(),
    "unmapped_details": tidy.loc[
        tidy["detail_clean"].notna() & tidy["detail_grouped"].eq(tidy["category"]),
        "detail_clean"
    ].nunique(),
}

pd.Series(checks).to_frame("value")
```

Export unmapped details for review:

```python
unmapped = (
    tidy.loc[tidy["detail_clean"].notna() & tidy["detail_grouped"].eq(tidy["category"])]
    .groupby(["category", "detail_clean"], dropna=False)
    .agg(count=("amount", "size"), total_amount=("amount", "sum"))
    .reset_index()
    .sort_values("total_amount", ascending=False)
)

unmapped.to_csv(QUALITY_DIR / "unmapped_details.csv", index=False)
```

### Section 12: Export clean CSV

```python
output_path = CLEAN_DIR / "personal_finance_transactions_clean.csv"
tidy.to_csv(output_path, index=False)
output_path
```

---

## 6. Recommended charts in Python

Yes, I recommend adding a few Python charts in the notebook, even if Tableau is the final visualization tool.

Use Python charts for data validation, not for the final dashboard.

Recommended notebook charts:

1. Monthly total spending
2. Monthly spending by major category
3. Top 15 detail groups by total amount
4. Operating vs capital spending over time
5. Recurring vs one-off spending over time
6. Heatmap: category by month

Example:

```python
monthly = tidy.groupby("year_month", as_index=False)["amount"].sum()

plt.figure(figsize=(12, 5))
sns.lineplot(data=monthly, x="year_month", y="amount", marker="o")
plt.xticks(rotation=45)
plt.title("Monthly Spending")
plt.tight_layout()
```

These charts help catch mistakes before Tableau. Tableau can then be used for the polished dashboard.

---

## 7. Tableau output recommendation

For Tableau, use the cleaned CSV only:

`data/cleaned/personal_finance_transactions_clean.csv`

Useful Tableau charts:

- spending by month;
- spending by category;
- spending by detail group;
- recurring vs one-off;
- operating vs capital;
- top merchants/details;
- monthly food/restaurants/groceries trend;
- shopping subtype breakdown.

Avoid connecting Tableau directly to the messy Excel workbook. It will make the Tableau side unnecessarily painful.

---

## 8. Implementation tasks

### Task 1: Create environment

Run:

```bash
cd /home/marcusai/MyProjects/PersonalFinanceTrackeing
python3 -m venv .venv
source .venv/bin/activate
pip install pandas openpyxl matplotlib seaborn jupyter
```

Verify:

```bash
python -c "import pandas, openpyxl, matplotlib, seaborn; print('ok')"
```

### Task 2: Create the new notebook

Create:

`01_clean_personal_finances.ipynb`

Add markdown sections:

1. Goal
2. Load raw Excel
3. Inspect raw structure
4. Remove summary rows
5. Standardize columns
6. Reshape wide-to-long
7. Clean details
8. Apply grouping rules
9. Add analysis columns
10. Data quality checks
11. Export clean CSV
12. Validation charts

### Task 3: Port useful mapping logic from old notebook

Copy the mapping dictionaries from `PersonalFinances.ipynb`, but clean them up:

- remove duplicate keys;
- use sets where values are ignored;
- avoid row-index patches;
- keep mapping rules near the transformation they support;
- add comments only where a decision is genuinely ambiguous.

### Task 4: Export quality reports

Create:

- `data/quality/unmapped_details.csv`
- `data/quality/cleaning_summary.csv`

These files make it easy to improve the mapping over time.

### Task 5: Export final Tableau CSV

Create:

`data/cleaned/personal_finance_transactions_clean.csv`

Acceptance criteria:

- one transaction per row;
- no missing dates;
- `amount` is numeric;
- no zero/negative spending rows unless intentionally kept;
- source row is preserved;
- date fields work in Tableau;
- detail grouping is good enough for first dashboard.

### Task 6: Add validation charts

Add quick charts to the bottom of the notebook.

Acceptance criteria:

- monthly totals chart renders;
- category-by-month chart renders;
- top detail groups chart renders;
- charts make obvious if a category mapping is wrong.

---

## 9. Main cleaning principle

Do not manually clean the Excel file.

Keep `personal_finances_raw.xlsx` as the messy-but-trusted source. Put every cleaning decision in Python so the process is repeatable when you update the spending document later.
