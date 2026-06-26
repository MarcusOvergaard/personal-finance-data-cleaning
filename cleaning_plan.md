# Public Cleaning Plan

## Goal

Clean the public sample export into a usable transaction dataset using the same core logic as the private project.

## Inputs

Primary sample input:
- `data/sample/raw_transactions_sample.csv`

Reference rules:
- `data/reference/classification_rules.csv`

## Outputs

Generated outputs:
- `data/sample/cleaned_transactions_sample.csv`
- `data/quality/cleaning_summary_sample.csv`
- `data/quality/unmapped_details_sample.csv`
- `images/dashboard_overview.png`
- `images/dashboard_monthly.png`
- `images/dashboard_categories.png`
- `images/workflow.png`

## Pipeline design

1. Load the messy raw export without assuming a clean header
2. Skip header / summary rows
3. Forward-fill dates for continuation rows
4. Reshape wide category columns into one transaction per row
5. Normalize free-text detail values
6. Apply exact rules from `classification_rules.csv`
7. Apply keyword fallbacks for obvious variants
8. Mark unresolved details as `needs_review`
9. Export a clean sample dataset and quality review files
10. Generate dashboard preview images from the cleaned sample

## Why the raw sample is CSV

The original private source was an Excel workbook.

The sample is a CSV because:
- it is easier to inspect on GitHub
- it still preserves the messy structural problems
- the pipeline logic stays nearly the same
- a text file is easier to review than a binary workbook, and it shows the same cleaning issues

## What the sample intentionally preserves

- inconsistent capitalization
- repeated merchant variants
- blank continuation dates
- malformed numeric formatting
- missing descriptions
- unresolved values that require analyst review

## What the sample intentionally removes

- all real financial history
- all real names and merchants
- all real dates and balances
- all identifying references from the original private workflow

## Rebuild command

```bash
python scripts/build_sample_assets.py
```

## Limitations

- The sample is synthetic, so the totals are only examples
- The Tableau screenshots are generated locally from the cleaned sample data. This repo includes the worksheet spec, not a packaged workbook.
