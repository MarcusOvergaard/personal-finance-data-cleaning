# Quality Checks

Outputs:
- `data/quality/cleaning_summary_sample.csv`
- `data/quality/unmapped_details_sample.csv`

## Summary checks

`cleaning_summary_sample.csv` records:
- total row count
- total income
- total expenses
- net cash flow
- date range
- missing dates
- missing amounts
- count of rows marked `needs_review`
- count of unique unresolved details

## Unmapped review queue

`unmapped_details_sample.csv` lists unresolved normalized detail values with:
- category
- count
- total amount
- first date
- last date
- similar existing rule

This is the manual review queue for tightening the classification rules.

## Expected healthy state

- `missing_dates = 0`
- `missing_amounts = 0`
- the unresolved list is short enough to review by hand

## Limitation

`needs_review` is not necessarily an error.

Sometimes that is intentional so the sample still shows a real review queue.
