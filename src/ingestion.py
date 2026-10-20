"""
Revio 2.0 Ingestion & Schema Validation Module
Parses and validates uploaded customer review CSV/JSON data with detailed error handling.
"""

from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
from datetime import datetime


REQUIRED_COLUMNS = ["review_text", "star_rating"]
OPTIONAL_COLUMNS = ["branch_name", "date", "customer_name", "platform"]


class IngestionError(Exception):
    """Custom exception for ingestion and schema validation failures."""
    pass


def validate_and_parse_dataframe(df: pd.DataFrame, is_synthetic: bool = False) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Validates and standardizes a Pandas DataFrame into Revio 2.0 review records.

    Returns:
        Tuple of (clean_records, validation_metadata)
    """
    if df.empty:
        raise IngestionError("The uploaded file is empty. Please upload a CSV containing review rows.")

    # Normalize column names (lowercase, stripped)
    col_mapping = {}
    for col in df.columns:
        norm = str(col).strip().lower().replace(" ", "_")
        if norm in ["review", "review_text", "text", "comment", "feedback"]:
            col_mapping[col] = "review_text"
        elif norm in ["rating", "star_rating", "stars", "score"]:
            col_mapping[col] = "star_rating"
        elif norm in ["branch", "branch_name", "location", "store"]:
            col_mapping[col] = "branch_name"
        elif norm in ["date", "timestamp", "created_at"]:
            col_mapping[col] = "date"
        elif norm in ["customer", "customer_name", "author", "user"]:
            col_mapping[col] = "customer_name"
        elif norm in ["platform", "source", "channel"]:
            col_mapping[col] = "platform"

    df_renamed = df.rename(columns=col_mapping)
    if df_renamed.columns.duplicated().any():
        df_renamed = df_renamed.T.groupby(level=0).first().T

    # Check required columns
    missing_required = [c for c in REQUIRED_COLUMNS if c not in df_renamed.columns]
    if missing_required:
        raise IngestionError(
            f"Missing mandatory column(s): {', '.join(missing_required)}. "
            f"Expected schema: 'review_text', 'star_rating', optional 'branch_name', 'date'."
        )

    clean_records: List[Dict[str, Any]] = []
    dropped_count = 0
    error_details: List[str] = []

    for idx, row in df_renamed.iterrows():
        raw_text = row.get("review_text")
        raw_rating = row.get("star_rating")

        # 1. Validate review text
        if pd.isna(raw_text) or not str(raw_text).strip():
            dropped_count += 1
            error_details.append(f"Row {idx+1}: Empty or missing review_text")
            continue

        text = str(raw_text).strip()
        if len(text) < 3:
            dropped_count += 1
            error_details.append(f"Row {idx+1}: Review text too short (< 3 characters)")
            continue

        # 2. Validate star rating (must be integer 1 to 5)
        try:
            rating_val = float(raw_rating)
            rating = int(round(rating_val))
            if rating < 1 or rating > 5:
                dropped_count += 1
                error_details.append(f"Row {idx+1}: Rating {rating_val} out of bounds (must be 1-5)")
                continue
        except (ValueError, TypeError):
            dropped_count += 1
            error_details.append(f"Row {idx+1}: Non-numeric star_rating '{raw_rating}'")
            continue

        # 3. Handle optional attributes
        branch = str(row.get("branch_name", "Main Branch")).strip()
        if not branch or branch == "nan":
            branch = "Main Branch"

        cust_name = str(row.get("customer_name", f"Guest-{idx+1}")).strip()
        if not cust_name or cust_name == "nan":
            cust_name = f"Guest-{idx+1}"

        raw_date = row.get("date")
        if pd.isna(raw_date) or not str(raw_date).strip() or str(raw_date) == "nan":
            date_str = datetime.now().strftime("%Y-%m-%d")
        else:
            date_str = str(raw_date).strip()[:10]

        platform = str(row.get("platform", "Direct Upload")).strip()
        if not platform or platform == "nan":
            platform = "Direct Upload"

        record_id = str(row.get("id", f"REV-UP-{1000 + len(clean_records)}"))

        clean_records.append({
            "id": record_id,
            "customer_name": cust_name,
            "branch_id": f"BR-{hash(branch) % 1000:03d}",
            "branch_name": branch,
            "branch_city": "Registered Location",
            "platform": platform,
            "star_rating": rating,
            "timestamp": f"{date_str}T12:00:00",
            "date": date_str,
            "review_text": text,
            "is_synthetic": is_synthetic
        })

    if not clean_records:
        raise IngestionError(
            f"All {len(df)} rows in the file failed schema validation. "
            f"Sample errors: {'; '.join(error_details[:3])}"
        )

    metadata = {
        "total_rows_received": len(df),
        "valid_rows_retained": len(clean_records),
        "dropped_rows": dropped_count,
        "is_synthetic": is_synthetic,
        "sample_errors": error_details[:5]
    }

    return clean_records, metadata
