"""
Unit tests for Revio 2.0 CSV Ingestion & Schema Validation Engine
"""

import pytest
import pandas as pd
from src.ingestion import validate_and_parse_dataframe, IngestionError


def test_valid_csv_parsing():
    df = pd.DataFrame([
        {"review_text": "Food was delicious and service was fast.", "star_rating": 5, "branch_name": "Jaipur West"},
        {"review": "Wait time was too long, billing was confusing.", "stars": 2, "location": "Delhi South"}
    ])
    records, meta = validate_and_parse_dataframe(df, is_synthetic=False)
    assert len(records) == 2
    assert meta["valid_rows_retained"] == 2
    assert meta["dropped_rows"] == 0
    assert records[0]["branch_name"] == "Jaipur West"
    assert records[0]["star_rating"] == 5
    assert records[1]["branch_name"] == "Delhi South"
    assert records[1]["star_rating"] == 2
    assert records[0]["is_synthetic"] is False


def test_empty_dataframe_raises_error():
    df = pd.DataFrame()
    with pytest.raises(IngestionError, match="The uploaded file is empty"):
        validate_and_parse_dataframe(df)


def test_missing_required_column_raises_error():
    df = pd.DataFrame([
        {"branch_name": "Jaipur", "date": "2026-10-01"}
    ])
    with pytest.raises(IngestionError, match="Missing mandatory column"):
        validate_and_parse_dataframe(df)


def test_malformed_ratings_dropped():
    df = pd.DataFrame([
        {"review_text": "Valid review", "star_rating": 4},
        {"review_text": "Invalid rating 10", "star_rating": 10},
        {"review_text": "Invalid non-numeric", "star_rating": "not_a_number"},
        {"review_text": "", "star_rating": 5}
    ])
    records, meta = validate_and_parse_dataframe(df, is_synthetic=True)
    assert len(records) == 1
    assert meta["dropped_rows"] == 3
    assert records[0]["review_text"] == "Valid review"
    assert records[0]["is_synthetic"] is True
