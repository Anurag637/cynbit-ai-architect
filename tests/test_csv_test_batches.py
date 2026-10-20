"""
Automated Pipeline Verification Tests for Generated CSV Batches
Validates ingestion, ABSA decomposition, crisis detection, and analytics aggregation on both test files.
"""

import pytest
import pandas as pd
from pathlib import Path

from src.ingestion import validate_and_parse_dataframe
from src.analyzer import AspectSentimentAnalyzer
from src.crisis_detector import CrisisDetector
from src.response_generator import ResponseGenerator
from src.analytics import EnterpriseAnalyticsEngine
from src.config import BrandPersona, CrisisLevel


@pytest.fixture
def engines():
    return {
        "analyzer": AspectSentimentAnalyzer(),
        "detector": CrisisDetector(),
        "resp_gen": ResponseGenerator(),
        "analytics": EnterpriseAnalyticsEngine()
    }


def test_franchise_batch_csv_pipeline(engines):
    csv_path = Path("data/test_reviews_franchise_batch.csv")
    assert csv_path.exists(), "Franchise batch CSV file must exist"

    df = pd.read_csv(csv_path)
    records, meta = validate_and_parse_dataframe(df, is_synthetic=False)

    # 1. Ingestion assertions
    assert meta["total_rows_received"] == 16
    assert meta["valid_rows_retained"] == 16
    assert meta["dropped_rows"] == 0

    # 2. Analytics & ABSA assertions
    enriched = engines["analytics"].process_reviews(records)
    summary = engines["analytics"].generate_executive_summary(enriched)

    assert summary["total_reviews"] == 16
    assert 1.0 <= summary["avg_rating"] <= 5.0
    assert -1.0 <= summary["avg_sentiment"] <= 1.0
    assert len(summary["branch_rankings"]) >= 4

    # Verify aspects were detected
    aspect_health = summary["aspect_health"]
    assert "Customer Service" in aspect_health
    assert "Product & Food Quality" in aspect_health
    assert "Speed & Turnaround Time" in aspect_health

    # 3. Response Generation verification
    for r in enriched[:3]:
        analysis = engines["analyzer"].analyze(r["review_text"], r["star_rating"])
        crisis = engines["detector"].evaluate(r["review_text"], r["star_rating"])
        resp = engines["resp_gen"].generate(
            customer_name=r["customer_name"],
            branch_name=r["branch_name"],
            analysis=analysis,
            crisis=crisis,
            persona=BrandPersona.EMPATHETIC_RESOLUTION,
            use_llm_if_available=False
        )
        assert resp.response_text is not None
        assert resp.guardrail_passed is True
        assert len(resp.actionable_steps) >= 1


def test_crisis_and_edge_cases_csv_pipeline(engines):
    csv_path = Path("data/test_reviews_crisis_and_edge_cases.csv")
    assert csv_path.exists(), "Crisis and edge cases CSV file must exist"

    df = pd.read_csv(csv_path)
    records, meta = validate_and_parse_dataframe(df, is_synthetic=False)

    # 1. Schema Validation & Malformed Row Dropping
    assert meta["total_rows_received"] == 17
    assert meta["valid_rows_retained"] == 14
    assert meta["dropped_rows"] == 3
    assert len(meta["sample_errors"]) == 3
    # Check that the malformed reasons are accurately captured
    assert any("Empty or missing review_text" in err for err in meta["sample_errors"])
    assert any("Rating 9.0 out of bounds" in err for err in meta["sample_errors"])
    assert any("Non-numeric star_rating" in err for err in meta["sample_errors"])

    # 2. Crisis Interception & Threat Vector Assertions
    enriched = engines["analytics"].process_reviews(records)
    summary = engines["analytics"].generate_executive_summary(enriched)

    assert summary["crisis_count"] >= 7
    assert summary["crisis_pct"] >= 50.0

    # Specifically verify critical health, fraud, harassment, and police cases
    food_poisoning_case = next(r for r in enriched if "food poisoning" in r["review_text"].lower())
    assert food_poisoning_case["crisis_level"] == "CRITICAL"
    assert food_poisoning_case["risk_score"] >= 80
    assert "Health, Hygiene & Safety Violation" in food_poisoning_case["threat_vectors"]

    fraud_case = next(r for r in enriched if "unauthorized charge" in r["review_text"].lower())
    assert fraud_case["crisis_level"] in ["HIGH", "CRITICAL"]
    assert "Financial Integrity & Fraud Allegation" in fraud_case["threat_vectors"]

    abuse_case = next(r for r in enriched if "abusive language" in r["review_text"].lower())
    assert abuse_case["crisis_level"] in ["HIGH", "CRITICAL"]
    assert "Harassment & Human Safety" in abuse_case["threat_vectors"]

    police_case = next(r for r in enriched if "fir" in r["review_text"].lower())
    assert police_case["crisis_level"] in ["HIGH", "CRITICAL"]
    assert "Legal & Regulatory Action" in police_case["threat_vectors"]

    # 3. Verify Human-in-the-Loop Routing for Crisis Reviews
    for r in enriched:
        if r["is_crisis"]:
            analysis = engines["analyzer"].analyze(r["review_text"], r["star_rating"])
            crisis = engines["detector"].evaluate(r["review_text"], r["star_rating"])
            resp = engines["resp_gen"].generate(
                customer_name=r["customer_name"],
                branch_name=r["branch_name"],
                analysis=analysis,
                crisis=crisis,
                persona=BrandPersona.EXECUTIVE_ESCALATION,
                use_llm_if_available=False
            )
            assert resp.hitl_status == "REQUIRES_HUMAN_REVIEW"
            assert resp.ticket_id is not None
            assert "executive-care@cynbit.in" in resp.response_text or "care@cynbit.in" in resp.response_text
