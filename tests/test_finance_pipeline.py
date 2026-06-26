from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

from src.finance_pipeline import FINAL_COLUMNS, run_pipeline

ROOT = Path(__file__).resolve().parents[1]
RAW_SAMPLE = ROOT / "data" / "sample" / "raw_transactions_sample.csv"
RULES = ROOT / "data" / "reference" / "classification_rules.csv"
CLEANED_SAMPLE = ROOT / "data" / "sample" / "cleaned_transactions_sample.csv"
SUMMARY_SAMPLE = ROOT / "data" / "quality" / "cleaning_summary_sample.csv"
UNMAPPED_SAMPLE = ROOT / "data" / "quality" / "unmapped_details_sample.csv"


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def test_pipeline_rebuilds_tracked_outputs(tmp_path: Path) -> None:
    artifacts = run_pipeline(
        input_path=RAW_SAMPLE,
        rules_path=RULES,
        clean_output_path=tmp_path / "cleaned.csv",
        summary_output_path=tmp_path / "summary.csv",
        unmapped_output_path=tmp_path / "unmapped.csv",
    )

    expected_cleaned = _read_csv(CLEANED_SAMPLE)
    expected_summary = _read_csv(SUMMARY_SAMPLE)
    expected_unmapped = _read_csv(UNMAPPED_SAMPLE).fillna("")

    actual_cleaned = artifacts.cleaned.copy()
    actual_cleaned["date"] = actual_cleaned["date"].dt.strftime("%Y-%m-%d")
    actual_cleaned = actual_cleaned[expected_cleaned.columns].fillna("")
    expected_cleaned = expected_cleaned.fillna("")

    actual_unmapped = artifacts.unmapped.fillna("")

    assert_frame_equal(actual_cleaned.reset_index(drop=True), expected_cleaned.reset_index(drop=True), check_dtype=False)
    assert_frame_equal(artifacts.summary.reset_index(drop=True), expected_summary.reset_index(drop=True), check_dtype=False)
    assert_frame_equal(actual_unmapped.reset_index(drop=True), expected_unmapped.reset_index(drop=True), check_dtype=False)


def test_cleaned_sample_has_portfolio_shape() -> None:
    cleaned = _read_csv(CLEANED_SAMPLE)

    assert list(cleaned.columns) == FINAL_COLUMNS
    assert 100 <= len(cleaned) <= 300
    assert bool(cleaned["date"].notna().all())
    assert bool(cleaned["amount"].gt(0).all())
    assert bool(cleaned["classification_source"].eq("needs_review").any())
    assert cleaned["detail_grouped"].eq("needs_review").sum() <= 25
