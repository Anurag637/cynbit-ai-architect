"""
Test script to execute the exact test cases outlined in Master Prompt Phases 5, 6, 7 & 8.
"""

from src.analyzer import AspectSentimentAnalyzer
from src.crisis_detector import CrisisDetector
from src.response_generator import ResponseGenerator
from src.config import BrandPersona

analyzer = AspectSentimentAnalyzer()
detector = CrisisDetector()
resp_gen = ResponseGenerator()

print("=" * 70)
print("  PHASE 5: ASPECT-BASED SENTIMENT ANALYSIS TESTS")
print("=" * 70)
phase5_tests = [
    ("The food was excellent, but the staff were rude.", 3),
    ("The service was not bad.", 3),
    ("The restaurant was not clean.", 1),
    ("The staff were not rude, but the billing was incorrect.", 2),
    ("Lajawab food, lekin delivery bahut late thi.", 3),
    ("I love waiting two hours for cold food.", 1),
    ("The food was good and the bill was correct.", 5)
]

for text, rating in phase5_tests:
    res = analyzer.analyze(text, rating)
    asps = [(a.category, a.sentiment.value, round(a.score, 2)) for a in res.detected_aspects]
    print(f"Review: \"{text}\" ({rating} stars)")
    print(f"  Result Sentiment: {res.overall_sentiment.value} ({res.compound_score:+.2f})")
    print(f"  Aspects Detected: {asps}")
    print()

print("=" * 70)
print("  PHASE 6: CRISIS AND URGENCY DETECTION TESTS")
print("=" * 70)
phase6_tests = [
    ("I became ill after eating here and have been vomiting since last night.", 1),
    ("Nobody threatened me.", 5),
    ("I am considering legal action because the manager threatened me.", 1),
    ("Does this sauce contain peanuts? I have a severe peanut allergy.", 2),
    ("The food was good, but the cashier charged my card twice.", 2),
    ("I did not get food poisoning.", 5),
    ("The restaurant was clean and the staff were helpful.", 5)
]

for text, rating in phase6_tests:
    crisis = detector.evaluate(text, rating)
    print(f"Review: \"{text}\" ({rating} stars)")
    print(f"  Risk Score: {crisis.risk_score}% | Tier: {crisis.crisis_level.value}")
    print(f"  Threat Vectors: {crisis.threat_vectors}")
    print(f"  Matched Triggers: {crisis.matched_triggers}")
    print(f"  SLA Target: {crisis.sla_window} -> {crisis.escalation_target}")
    print()
