# Classification Rules Reference

File:
- `data/reference/classification_rules.csv`

## Purpose

This file stores exact mappings from normalized transaction detail text to grouped analytical categories.

It keeps the classification logic editable outside the notebook.

## Columns

- `category_scope` — optional source category restriction such as `food` or `income`
- `detail_clean` — normalized text key used for exact matching
- `detail_grouped` — grouped analytical label
- `shopping_type` — optional sub-type for shopping rows
- `expense_type_override` — optional override such as `capital` or `income`
- `recurrence_override` — optional override such as `recurring` or `one_off`
- `note` — documentation for the rule source

## Matching order

The pipeline applies rules in this order:
1. category-specific exact match
2. global exact match
3. keyword fallback rule
4. unresolved -> `needs_review`

## Maintenance guidance

When a new unresolved detail appears:
1. inspect `data/quality/unmapped_details_sample.csv`
2. decide whether it belongs under an existing grouped label
3. add a new exact rule if the label is stable
4. rerun the pipeline

## Public-repo convention

Rules in this repository use fictional labels only.

If you maintain a private version locally, keep any sensitive exact mappings outside the public repository.