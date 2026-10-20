"""
Unit tests for Revio 2.0 Response Generator & Guardrails
"""

import pytest
from src.analyzer import AspectSentimentAnalyzer
from src.crisis_detector import CrisisDetector
from src.response_generator import ResponseGenerator
from src.config import BrandPersona, CrisisLevel


@pytest.fixture
def response_gen():
    return ResponseGenerator()


@pytest.fixture
def analyzer():
    return AspectSentimentAnalyzer()


@pytest.fixture
def detector():
    return CrisisDetector()


def test_positive_response_auto_approval(response_gen, analyzer, detector):
    text = "Superb service and delicious pizza!"
    analysis = analyzer.analyze(text, star_rating=5)
    crisis = detector.evaluate(text, star_rating=5)
    resp = response_gen.generate(
        customer_name="Aditi Rao",
        branch_name="Jaipur Flagship",
        analysis=analysis,
        crisis=crisis,
        persona=BrandPersona.WARM_CONCILIATORY
    )
    assert resp.hitl_status == "AUTO_APPROVED"
    assert "Jaipur Flagship" in resp.response_text
    assert resp.guardrail_passed is True


def test_critical_crisis_hitl_and_ticket_generation(response_gen, analyzer, detector):
    text = "Severe food poisoning after eating here. Hospitalized overnight."
    analysis = analyzer.analyze(text, star_rating=1)
    crisis = detector.evaluate(text, star_rating=1)
    resp = response_gen.generate(
        customer_name="Rohan Verma",
        branch_name="Gurugram CyberCity",
        analysis=analysis,
        crisis=crisis,
        persona=BrandPersona.EXECUTIVE_ESCALATION
    )
    assert resp.hitl_status == "REQUIRES_HUMAN_REVIEW"
    assert resp.ticket_id is not None
    assert f"#{resp.ticket_id}" in resp.response_text
    assert "executive-care@cynbit.in" in resp.response_text
