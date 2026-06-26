# Privacy Decisions

## Goal

Show the cleaning and governance work without exposing any real financial history.

## What was removed from the public version

Not published:
- real transactions
- real merchant names
- real balances
- real income values
- real dates
- real family / personal labels
- the original private workbook
- the older exploratory notebook with saved outputs

## Why synthetic data was used

Simple redaction is not enough for personal finance data.

Even when names are removed, combinations of:
- exact dates
- unusual amounts
- recurring charges
- location hints
- family references

can still make records identifiable.

Synthetic sample data avoids that problem while keeping the same cleanup problems:
- messy text values
- duplicated merchant variants
- blank continuation dates
- inconsistent spacing and capitalization
- unresolved descriptions
- malformed numeric formatting

## What stayed the same

The public version keeps the same core cleanup steps:
- noisy raw export
- header removal
- date forward-fill
- wide-to-tidy reshaping
- text normalization
- rule-based categorization
- quality review exports

## Publication policy for future updates

If this project changes later, only publish:
1. synthetic sample data
2. generic rules with fictional examples
3. screenshots built from synthetic data
4. aggregated documentation that contains no real financial details

Do not publish row-level data derived from the private workbook.
