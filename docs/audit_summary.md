# Publication Audit Summary

This is a snapshot of the repo before the public cleanup.

## 1. Repository state before changes

Original tracked files:
- `01_clean_personal_finances.ipynb`
- `PersonalFinances.ipynb`
- `README.md`
- `cleaning_plan.md`
- `data/reference/classification_rules.csv`
- `requirements.txt`

Original untracked local files present during the audit:
- `personal_finances_raw.xlsx`
- `data/cleaned/personal_finance_transactions_clean.csv`
- `data/quality/cleaning_summary.csv`
- `data/quality/unmapped_details.csv`

Git state during audit:
- branch: `main`
- tracked history: one initial commit
- no remote configured

## 2. Inputs, outputs, and pipeline found

Input found:
- `personal_finances_raw.xlsx` — private household finance workbook in a wide layout

Outputs found:
- `data/cleaned/personal_finance_transactions_clean.csv`
- `data/quality/cleaning_summary.csv`
- `data/quality/unmapped_details.csv`

Pipeline found in the working notebook:
1. read the raw workbook
2. drop header / summary rows
3. keep useful columns only
4. forward-fill blank dates
5. reshape wide category columns into one transaction per row
6. normalize text details
7. apply classification rules
8. derive expense metadata
9. export tidy CSV and review files

Rule-based categorization found:
- exact detail mappings in `data/reference/classification_rules.csv`
- additional hard-coded logic in notebooks
- unresolved details exported for manual review

## 3. Existing documentation found

Present during audit:
- `README.md`
- `cleaning_plan.md`
- notebook markdown in `01_clean_personal_finances.ipynb`

Missing during audit:
- public privacy note
- recruiter-oriented README framing
- screenshot assets
- sample public dataset
- dashboard documentation built for a public repo

## 4. Privacy exposure found

Tracked privacy leaks in the pre-public version:
- `PersonalFinances.ipynb` contained saved outputs with real transaction examples
- `data/reference/classification_rules.csv` contained personal and location-specific labels from the private workflow
- docs referenced local paths and private examples

Local but untracked privacy leaks found:
- raw private workbook
- cleaned row-level transactions
- quality outputs showing dates, amounts, and unresolved private labels

Sensitive fields or patterns observed:
- real dates
- real merchant strings
- real amounts
- family / personal labels
- location-specific labels
- review queues containing unresolved private text

## 5. Publication risks

Main risk:
In its original form, the repo was not safe to publish because the notebook and rule file exposed private financial data.

Secondary risk:
`.gitignore` protected some local files from future commits, but it did not solve already-tracked private content.

## 6. Public-safe design chosen

Decision:
Use synthetic sample data instead of trying to anonymize real transactions.

Why:
- safer than attempting to redact real transactions one by one
- preserves the cleaning and validation story
- keeps the pipeline reproducible
- avoids accidental re-identification through dates, amounts, and merchant combinations

Core refactor decisions:
- remove the old private notebook from tracked files
- replace tracked rules with fictional shareable rules
- add public sample raw and cleaned datasets
- document privacy choices explicitly
- keep the wide-to-tidy cleaning pattern intact

## 7. Remaining limitation

I could not build a Tableau workbook here because Tableau was not available in WSL.


The repository now includes:
- cleaned Tableau-ready sample data
- dashboard screenshots generated from that data
- a worksheet specification for reproducing the dashboard in Tableau
