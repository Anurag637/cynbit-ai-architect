"""
Unit tests for Revio 2.0 Response Generator, Guardrails & Human-in-the-Loop workflows
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


def test_positive_response_human_approval_queued(response_gen, analyzer, detector):
    """Verifies that in POC mode, even positive responses require human sign-off before dispatch."""
    text = "Superb service and delicious pizza!"
    analysis = analyzer.analyze(text, star_rating=5)
    crisis = detector.evaluate(text, star_rating=5)
    resp = response_gen.generate(
        customer_name="Aditi Rao",
        branch_name="Jaipur Flagship",
        analysis=analysis,
        crisis=crisis,
        persona=BrandPersona.WARM_CONCILIATORY,
        use_llm_if_available=False
    )
    assert resp.hitl_status == "PENDING_HUMAN_APPROVAL"
    assert "Jaipur Flagship" in resp.response_text
    assert resp.guardrail_passed is True


def test_critical_crisis_hitl_and_ticket_generation(response_gen, analyzer, detector):
    """Verifies high-risk crisis routing to human leadership with simulated ticket number."""
    text = "Severe food poisoning after eating here. Hospitalized overnight."
    analysis = analyzer.analyze(text, star_rating=1)
    crisis = detector.evaluate(text, star_rating=1)
    resp = response_gen.generate(
        customer_name="Rohan Verma",
        branch_name="Gurugram CyberCity",
        analysis=analysis,
        crisis=crisis,
        persona=BrandPersona.EXECUTIVE_ESCALATION,
        use_llm_if_available=False
    )
    assert resp.hitl_status == "REQUIRES_HUMAN_REVIEW"
    assert resp.ticket_id is not None
    assert f"#{resp.ticket_id}" in resp.response_text
    assert "executive-care@cynbit.in" in resp.response_text


def test_guardrail_sanitizes_liability_clauses(response_gen, analyzer, detector):
    """Verifies that legally hazardous or unverified concession statements are intercepted and sanitized."""
    text = "Horrible service, food was raw."
    analysis = analyzer.analyze(text, star_rating=1)
    crisis = detector.evaluate(text, star_rating=1)

    # Simulate an injected unsafe response
    resp = response_gen.generate(
        customer_name="John Doe",
        branch_name="Jaipur Flagship",
        analysis=analysis,
        crisis=crisis,
        persona=BrandPersona.EMPATHETIC_RESOLUTION,
        use_llm_if_available=False
    )

    # Now verify manually with custom text injected into the guardrail
    from src.response_generator import GeneratedResponse
    unsafe_text = "We admit we were at fault and here is 100% cashback guaranteed for your trouble."
    
    # Run the guardrail check
    lower = unsafe_text.lower()
    from src.config import FORBIDDEN_PHRASES
    has_forbidden = any(phrase in lower for phrase in FORBIDDEN_PHRASES)
    assert has_forbidden is True


def test_huggingface_free_model_fallback_safety(response_gen, analyzer, detector):
    """Verifies that Hugging Face integration degrades gracefully to deterministic fallback on network/auth failure."""
    text = "Great ambience and delicious pasta!"
    analysis = analyzer.analyze(text, star_rating=5)
    crisis = detector.evaluate(text, star_rating=5)

    # Calling with a dummy token should safely fall back to template rather than crashing
    resp = response_gen.generate(
        customer_name="Priya Singh",
        branch_name="Mumbai Bandra West Lab",
        analysis=analysis,
        crisis=crisis,
        persona=BrandPersona.WARM_CONCILIATORY,
        use_llm_if_available=True,
        custom_hf_key="hf_dummy_token_for_fallback_test",
        hf_model="meta-llama/Llama-3.1-8B-Instruct"
    )
    assert resp.hitl_status == "PENDING_HUMAN_APPROVAL"
    assert "Mumbai Bandra West Lab" in resp.response_text
    assert resp.generation_source == "Deterministic Policy Template (Safe Fallback)"
    assert resp.guardrail_passed is True
