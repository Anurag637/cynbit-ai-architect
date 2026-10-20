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
