# Personal Finance Tracking

A Python notebook project for cleaning a personal finance workbook into a tidy CSV for Tableau analysis.

## Project structure

- `01_clean_personal_finances.ipynb` — main cleaning notebook
- `PersonalFinances.ipynb` — older exploratory notebook kept for reference
- `cleaning_plan.md` — cleaning strategy and data model notes
- `data/reference/classification_rules.csv` — editable classification rules for transaction names
- `requirements.txt` — Python dependencies

## Workflow

1. Put the latest raw workbook in the project root as `personal_finances_raw.xlsx`.
2. Open `01_clean_personal_finances.ipynb`.
3. Run the notebook top to bottom.
4. Review `data/quality/unmapped_details.csv`.
5. Add or refine rules in `data/reference/classification_rules.csv`.
6. Rerun the notebook until the unresolved detail names are acceptable.
7. Use the cleaned CSV in Tableau.

## Environment

```bash
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

## Privacy note

The raw workbook and generated outputs are ignored by git by default so the repository is safer to publish. If you plan to make the repository public, also consider whether `data/reference/classification_rules.csv` contains personal detail names you do not want to share.
