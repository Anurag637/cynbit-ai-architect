"""
Unit tests for Revio 2.0 Aspect-Based Sentiment Analysis (ABSA) Engine
"""

import pytest
from src.analyzer import AspectSentimentAnalyzer
from src.config import Sentiment


@pytest.fixture
def analyzer():
    return AspectSentimentAnalyzer()


def test_positive_service_aspect(analyzer):
    text = "The staff was extremely polite and helpful during our dinner."
    analysis = analyzer.analyze(text, star_rating=5)
    assert analysis.overall_sentiment == Sentiment.POSITIVE
    assert analysis.compound_score > 0
    categories = [a.category for a in analysis.detected_aspects]
    assert "Customer Service" in categories
    aspect = next(a for a in analysis.detected_aspects if a.category == "Customer Service")
    assert aspect.sentiment == Sentiment.POSITIVE


def test_negative_speed_and_turnaround(analyzer):
    text = "Horrible delay, we waited 50 minutes for cold food."
    analysis = analyzer.analyze(text, star_rating=1)
    assert analysis.overall_sentiment == Sentiment.NEGATIVE
    assert analysis.compound_score < 0
    categories = [a.category for a in analysis.detected_aspects]
    assert "Speed & Turnaround Time" in categories


def test_mixed_sentiment_multi_aspect(analyzer):
    text = "The pasta was delicious and fresh, but the waiter was rude and arrogant."
    analysis = analyzer.analyze(text, star_rating=3)
    assert analysis.overall_sentiment == Sentiment.MIXED
    categories = [a.category for a in analysis.detected_aspects]
    assert "Product & Food Quality" in categories
    assert "Customer Service" in categories

    food_aspect = next(a for a in analysis.detected_aspects if a.category == "Product & Food Quality")
    service_aspect = next(a for a in analysis.detected_aspects if a.category == "Customer Service")

    assert food_aspect.sentiment == Sentiment.POSITIVE
    assert service_aspect.sentiment == Sentiment.NEGATIVE


def test_negation_inversion(analyzer):
    text = "The room was not clean and the soup was not warm."
    analysis = analyzer.analyze(text, star_rating=1)
    cleanliness_aspect = next((a for a in analysis.detected_aspects if a.category == "Cleanliness & Ambience"), None)
    if cleanliness_aspect:
        assert cleanliness_aspect.sentiment == Sentiment.NEGATIVE


def test_hinglish_aspect_sentiment(analyzer):
    text = "Khana ekdum bakwas tha aur staff bohot battameez tha."
    analysis = analyzer.analyze(text, star_rating=1)
    assert analysis.overall_sentiment == Sentiment.NEGATIVE
    categories = [a.category for a in analysis.detected_aspects]
    assert "Product & Food Quality" in categories
    assert "Customer Service" in categories
    food_asp = next(a for a in analysis.detected_aspects if a.category == "Product & Food Quality")
    assert food_asp.sentiment == Sentiment.NEGATIVE


def test_not_bad_service_negation(analyzer):
    text = "The service was not bad."
    analysis = analyzer.analyze(text, star_rating=3)
    service_asp = next(a for a in analysis.detected_aspects if a.category == "Customer Service")
    assert service_asp.sentiment == Sentiment.POSITIVE


def test_not_rude_staff_but_incorrect_billing(analyzer):
    text = "The staff were not rude, but the billing was incorrect."
    analysis = analyzer.analyze(text, star_rating=2)
    assert analysis.overall_sentiment == Sentiment.MIXED
    service_asp = next(a for a in analysis.detected_aspects if a.category == "Customer Service")
    bill_asp = next(a for a in analysis.detected_aspects if a.category == "Billing & Transactions")
    assert service_asp.sentiment == Sentiment.POSITIVE
    assert bill_asp.sentiment == Sentiment.NEGATIVE


def test_food_good_and_bill_correct(analyzer):
    text = "The food was good and the bill was correct."
    analysis = analyzer.analyze(text, star_rating=5)
    assert analysis.overall_sentiment == Sentiment.POSITIVE
    food_asp = next(a for a in analysis.detected_aspects if a.category == "Product & Food Quality")
    bill_asp = next(a for a in analysis.detected_aspects if a.category == "Billing & Transactions")
    assert food_asp.sentiment == Sentiment.POSITIVE
    assert bill_asp.sentiment == Sentiment.POSITIVE


def test_hinglish_lajawab_food_late_delivery(analyzer):
    text = "Lajawab food, lekin delivery bahut late thi."
    analysis = analyzer.analyze(text, star_rating=3)
    assert analysis.overall_sentiment == Sentiment.MIXED
    food_asp = next(a for a in analysis.detected_aspects if a.category == "Product & Food Quality")
    speed_asp = next(a for a in analysis.detected_aspects if a.category == "Speed & Turnaround Time")
    assert food_asp.sentiment == Sentiment.POSITIVE
    assert speed_asp.sentiment == Sentiment.NEGATIVE

