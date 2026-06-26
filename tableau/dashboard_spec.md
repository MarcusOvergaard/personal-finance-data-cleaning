# Tableau Dashboard Specification

This spec describes the Tableau dashboard shown in the sample screenshots.

Data source:
- `data/sample/cleaned_transactions_sample.csv`

## Required fields

Use these fields from the cleaned sample:
- `date`
- `year_month`
- `category`
- `transaction_direction`
- `amount`
- `signed_amount`
- `detail_grouped`

## Calculated fields

1. `Expense Amount`
   - `IF [transaction_direction] = 'expense' THEN [amount] END`

2. `Income Amount`
   - `IF [transaction_direction] = 'income' THEN [amount] END`

3. `Savings`
   - `SUM([Income Amount]) - SUM([Expense Amount])`

4. `Savings Rate`
   - `IF SUM([Income Amount]) = 0 THEN 0 ELSE (SUM([Income Amount]) - SUM([Expense Amount])) / SUM([Income Amount]) END`

## Worksheets

### 1. Monthly Spending
- Columns: `year_month`
- Rows: `SUM([Expense Amount])`, `SUM([Income Amount])`
- Marks: line
- Purpose: monthly trend of income vs expenses

### 2. Spending by Category
- Filter: `transaction_direction = expense`
- Rows: `category`
- Columns: `SUM([amount])`
- Sort descending by amount
- Marks: bar

### 3. Top Merchants
- Filter: `transaction_direction = expense`
- Rows: `detail_grouped`
- Columns: `SUM([amount])`
- Keep top 8 by amount
- Marks: bar

### 4. Savings Rate
- Columns: `year_month`
- Rows: `AVG([Savings Rate])`
- Marks: bar
- Format axis as percent

## Dashboard layout

Arrange the four sheets in a 2x2 dashboard:
- top left: Monthly Spending
- top right: Spending by Category
- bottom left: Top Merchants
- bottom right: Savings Rate

## Why this is a spec instead of a packaged workbook

A Tableau runtime was not available in the local WSL environment used for this refactor.

So the repo includes:
- a clean Tableau-ready CSV
- reproducible screenshot assets built from the same dataset
- this worksheet setup so you can rebuild it quickly in Tableau Desktop or Tableau Public
