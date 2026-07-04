# Personal Finance Tracking

This project cleans and analyzes a messy household finance export into an analysis-ready dataset using synthetic sample data for privacy.

## Project Overview

The project centers on a notebook that cleans, explores, and analyzes a messy household finance export. The repository also includes a supporting pipeline used to generate the public sample dataset.

## Skills Demonstrated

- Python data cleaning with pandas
- Data transformation and reshaping
- Exploratory data analysis
- Tableau dashboard development

## Dataset

The original household finance data is intentionally excluded from this repository.

A synthetic sample dataset reproduces the same structural challenges while protecting personal financial information.

## Methodology

Raw transaction export
        ↓
Clean and reshape
        ↓
Categorize transactions
        ↓
Analyze spending
        ↓
Create dashboard

## Getting Started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_sample_assets.py
```

## Dashboard
Python visualizations were used during exploratory analysis, while the final interactive dashboard was built in Tableau.

Interactive Tableau dashboards: [(https://public.tableau.com/app/profile/marcus.timm/viz/PersonalFinanceTracking_17825656373810/Dashboard)]

![Dashboard Overview](images/dashboard_overview.png)

![Monthly View](images/dashboard_monthly.png)

![Category View](images/dashboard_categories.png)

## Limitations

The project uses synthetic sample data that preserves the structure of the original dataset but does not reflect real financial activity.

## Future Improvements

- Add automated tests for the pipeline module
- Add a packaged Tableau workbook when there is a workable way to generate one
- Expand quality checks for duplicate detection and schema validation
- Separate private and public classification rules
