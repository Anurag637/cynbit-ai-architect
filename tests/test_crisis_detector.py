"""
Unit tests for Revio 2.0 Crisis & Urgency Detection Engine
"""

import pytest
from src.crisis_detector import CrisisDetector
from src.config import CrisisLevel


@pytest.fixture
def detector():
    return CrisisDetector()


def test_critical_food_poisoning_detection(detector):
    text = "We ended up in the hospital with severe food poisoning after eating the fish."
    eval_result = detector.evaluate(text, star_rating=1)
    assert eval_result.crisis_level == CrisisLevel.CRITICAL
    assert eval_result.risk_score >= 80
    assert "Health, Hygiene & Safety Violation" in eval_result.threat_vectors
    assert "< 15 Minutes" in eval_result.sla_window


def test_legal_threat_detection(detector):
    text = "The manager threatened us and refused to give a receipt. My lawyer is filing a lawsuit in consumer court."
    eval_result = detector.evaluate(text, star_rating=1)
    assert eval_result.crisis_level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL]
    assert "Legal & Regulatory Action" in eval_result.threat_vectors


def test_routine_positive_review_low_risk(detector):
    text = "Everything was superb! Quick service, friendly crew, and great coffee."
    eval_result = detector.evaluate(text, star_rating=5)
    assert eval_result.crisis_level == CrisisLevel.LOW
    assert eval_result.risk_score < 35
    assert "Automated AI Brand Agent" in eval_result.escalation_target


def test_negated_threat_and_food_poisoning(detector):
    # Negated phrases must not trigger false positive crisis alarms
    negated_abuse = detector.evaluate("Nobody threatened me.", star_rating=5)
    assert negated_abuse.crisis_level == CrisisLevel.LOW
    assert negated_abuse.risk_score == 0
    assert "Harassment & Human Safety" not in negated_abuse.threat_vectors
    assert negated_abuse.threat_vectors == ["Routine Feedback"]

    negated_illness = detector.evaluate("I did not get food poisoning.", star_rating=5)
    assert negated_illness.crisis_level == CrisisLevel.LOW
    assert negated_illness.risk_score == 0
    assert "Health, Hygiene & Safety Violation" not in negated_illness.threat_vectors


def test_allergy_crisis_detection(detector):
    text = "Does this sauce contain peanuts? I have a severe peanut allergy."
    eval_result = detector.evaluate(text, star_rating=2)
    assert eval_result.crisis_level == CrisisLevel.CRITICAL
    assert "Health, Hygiene & Safety Violation" in eval_result.threat_vectors


def test_double_charge_financial_integrity(detector):
    text = "The food was good, but the cashier charged my card twice."
    eval_result = detector.evaluate(text, star_rating=2)
    assert eval_result.crisis_level == CrisisLevel.HIGH
    assert "Financial Integrity & Fraud Allegation" in eval_result.threat_vectors
