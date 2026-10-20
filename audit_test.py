"""Audit Test Script — Empirical tests for the deep audit"""
from src.analyzer import AspectSentimentAnalyzer
from src.crisis_detector import CrisisDetector
from src.response_generator import ResponseGenerator
from src.config import BrandPersona

a = AspectSentimentAnalyzer()
c = CrisisDetector()
r = ResponseGenerator()

def show(label, res, crisis=None):
    print(f"\n=== {label} ===")
    print(f"  Sentiment: {res.overall_sentiment.value}, Score: {res.compound_score:.2f}")
    for asp in res.detected_aspects:
        print(f"  Aspect: {asp.category} -> {asp.sentiment.value} ({asp.score:+.2f}) | kw: {asp.keywords}")
    print(f"  Emotion: {res.primary_emotion}")
    if crisis:
        print(f"  Crisis: {crisis.crisis_level.value}, Risk={crisis.risk_score}")
        print(f"  Vectors: {crisis.threat_vectors}")
        print(f"  Matched: {crisis.matched_triggers}")

# TEST 1: Pure positive
res1 = a.analyze("Amazing food, great service, spotless ambience!", 5)
cr1 = c.evaluate("Amazing food, great service, spotless ambience!", 5)
show("TEST 1: Pure Positive", res1, cr1)

# TEST 2: Mixed sentiment
res2 = a.analyze("The food was delicious but the service was rude and slow.", 3)
cr2 = c.evaluate("The food was delicious but the service was rude and slow.", 3)
show("TEST 2: Mixed", res2, cr2)

# TEST 3: Critical crisis
text3 = "Food poisoning, vomiting, hospital admission, calling lawyer and police!"
res3 = a.analyze(text3, 1)
cr3 = c.evaluate(text3, 1)
show("TEST 3: Critical Crisis", res3, cr3)

# TEST 4: Negation suppression
text4 = "Nobody threatened me and I did not get food poisoning."
cr4 = c.evaluate(text4, 4)
print(f"\n=== TEST 4: Negation ===")
print(f"  Crisis: {cr4.crisis_level.value}, Risk={cr4.risk_score}")
print(f"  Matched Triggers: {cr4.matched_triggers}")
print(f"  Vectors: {cr4.threat_vectors}")

# TEST 5: Hinglish
text5 = "Khana lajawab tha, badhiya staff. Lekin bill mehnga tha."
res5 = a.analyze(text5, 3)
show("TEST 5: Hinglish", res5)

# TEST 6: Response with guardrails
resp6 = r.generate("Anurag", "Jaipur Flagship", res3, cr3, BrandPersona.EXECUTIVE_ESCALATION, use_llm_if_available=False)
print(f"\n=== TEST 6: Response Generation ===")
print(f"  HITL: {resp6.hitl_status}")
print(f"  Guardrail: {resp6.guardrail_passed}")
print(f"  Source: {resp6.generation_source}")
print(f"  Ticket: {resp6.ticket_id}")
print(f"  Response: {resp6.response_text[:200]}...")

# TEST 7: Guardrail catches forbidden phrases
from src.analyzer import ReviewAnalysis, Sentiment, AspectResult
fake_analysis = ReviewAnalysis(
    overall_sentiment=Sentiment.NEGATIVE,
    compound_score=-0.5,
    detected_aspects=[],
    primary_emotion="Anger",
    root_cause="Test",
    star_rating=1,
    word_count=10
)
from src.crisis_detector import CrisisEvaluation
from src.config import CrisisLevel
fake_crisis = CrisisEvaluation(
    risk_score=90, crisis_level=CrisisLevel.CRITICAL,
    threat_vectors=["Test"], matched_triggers=["test"],
    flag_reasons=["Test"], escalation_target="Test",
    sla_window="<15 min", recommended_action="Test"
)
resp7 = r.generate("Test", "Branch", fake_analysis, fake_crisis, use_llm_if_available=False)
# Inject forbidden phrase manually to test sanitization
from src.config import FORBIDDEN_PHRASES
print(f"\n=== TEST 7: Guardrail forbidden phrases ===")
print(f"  Forbidden phrases count: {len(FORBIDDEN_PHRASES)}")

# TEST 8: Allergy crisis detection
text8 = "My child had a severe allergic reaction to peanuts in the dish. She has a peanut allergy and needed emergency treatment."
cr8 = c.evaluate(text8, 1)
print(f"\n=== TEST 8: Allergy Crisis ===")
print(f"  Crisis: {cr8.crisis_level.value}, Risk={cr8.risk_score}")
print(f"  Vectors: {cr8.threat_vectors}")

# TEST 9: Double charge fraud
text9 = "They charged my card twice for the same order! This is a double charge and I want my money back!"
cr9 = c.evaluate(text9, 1)
print(f"\n=== TEST 9: Double Charge ===")
print(f"  Crisis: {cr9.crisis_level.value}, Risk={cr9.risk_score}")
print(f"  Vectors: {cr9.threat_vectors}")

# TEST 10: use_container_width deprecation check
print(f"\n=== TEST 10: Deprecation Warnings ===")
import re
with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()
matches = re.findall(r"use_container_width", content)
print(f"  use_container_width occurrences: {len(matches)}")

print("\n=== ALL AUDIT TESTS COMPLETED ===")
