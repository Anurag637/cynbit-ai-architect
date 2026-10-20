"""
Revio 2.0 Crisis Detection & Urgency Triage Engine
Evaluates legal liabilities, health & safety violations, fraud allegations, and viral PR threats.

Screening Philosophy & Guardrail Notes:
- Scores represent heuristic screening estimates (0-100) calibrated for high recall on critical risks,
  ensuring severe complaints receive immediate human manager escalation.
- Scores are NOT frequentist probabilities and should not be presented as calibrated statistical likelihoods.
- High recall design minimizes critical false negatives, but may occasionally flag metaphorical frustration
  (e.g., 'this bill gave me a heart attack'), which is why Human-in-the-Loop review is mandatory.
"""

import re
from typing import Dict, List
from src.config import CRISIS_TRIGGERS, CrisisLevel


class CrisisEvaluation:
    def __init__(
        self,
        risk_score: int,
        crisis_level: CrisisLevel,
        threat_vectors: List[str],
        matched_triggers: List[str],
        flag_reasons: List[str],
        escalation_target: str,
        sla_window: str,
        recommended_action: str
    ):
        self.risk_score = risk_score
        self.crisis_level = crisis_level
        self.threat_vectors = threat_vectors
        self.matched_triggers = matched_triggers
        self.flag_reasons = flag_reasons
        self.escalation_target = escalation_target
        self.sla_window = sla_window
        self.recommended_action = recommended_action

    def to_dict(self) -> Dict:
        return {
            "risk_score": self.risk_score,
            "crisis_level": self.crisis_level.value,
            "threat_vectors": self.threat_vectors,
            "matched_triggers": self.matched_triggers,
            "flag_reasons": self.flag_reasons,
            "escalation_target": self.escalation_target,
            "sla_window": self.sla_window,
            "recommended_action": self.recommended_action,
            "is_screening_estimate": True
        }


class CrisisDetector:
    """Enterprise risk scoring engine with deterministic rule weights and evidence-matched vector clustering."""

    def __init__(self):
        self.triggers = CRISIS_TRIGGERS

    def evaluate(self, text: str, star_rating: int = 3) -> CrisisEvaluation:
        lower_text = text.lower()
        score = 0
        matched: List[str] = []
        vectors: List[str] = []
        flag_reasons: List[str] = []

        # 1. Base score from star rating
        if star_rating == 1:
            score += 25
        elif star_rating == 2:
            score += 15
        elif star_rating == 3:
            score += 5

        # 2. Check matched crisis triggers
        for trigger, weight in self.triggers.items():
            if re.search(r'\b' + re.escape(trigger) + r'\b', lower_text):
                score += weight
                matched.append(trigger)

        # 3. Categorize threat vectors with matched evidence
        legal_kws = ["lawyer", "legal action", "sue", "lawsuit", "court", "consumer court", "consumer forum", "police", "fir", "fssai"]
        health_kws = ["food poisoning", "vomiting", "hospital", "sick", "illness", "cockroach", "rat", "maggot", "contaminated", "zehar", "poison", "infection", "expired"]
        fraud_kws = ["fraud", "scam", "cheating", "stole", "theft", "unauthorized charge", "chori", "dhoka", "thug", "robbery"]
        abuse_kws = ["harassment", "assault", "discriminate", "racist", "casteist", "abuse", "threatened", "gunda"]
        viral_kws = ["twitter", "viral", "instagram", "post online", "municipal", "media", "news"]

        matched_legal = [k for k in legal_kws if re.search(r'\b' + re.escape(k) + r'\b', lower_text)]
        if matched_legal:
            vectors.append("Legal & Regulatory Action")
            flag_reasons.append(f"Legal Escalation: customer mentioned legal remedies ({', '.join(matched_legal)})")

        matched_health = [k for k in health_kws if re.search(r'\b' + re.escape(k) + r'\b', lower_text)]
        if matched_health:
            vectors.append("Health, Hygiene & Safety Violation")
            flag_reasons.append(f"Health & Safety Hazard: health symptoms or contamination mentioned ({', '.join(matched_health)})")

        matched_fraud = [k for k in fraud_kws if re.search(r'\b' + re.escape(k) + r'\b', lower_text)]
        if matched_fraud:
            vectors.append("Financial Integrity & Fraud Allegation")
            flag_reasons.append(f"Financial / Fraud Allegation: billing integrity compromised ({', '.join(matched_fraud)})")

        matched_abuse = [k for k in abuse_kws if re.search(r'\b' + re.escape(k) + r'\b', lower_text)]
        if matched_abuse:
            vectors.append("Harassment & Human Safety")
            flag_reasons.append(f"Safety & Discrimination: abusive behavior or harassment reported ({', '.join(matched_abuse)})")

        matched_viral = [k for k in viral_kws if re.search(r'\b' + re.escape(k) + r'\b', lower_text)]
        if matched_viral:
            vectors.append("Public Viral PR Exposure")
            flag_reasons.append(f"Viral Escalation: public media or social platform exposure threatened ({', '.join(matched_viral)})")

        # Cap score between 0 and 100
        risk_score = min(100, max(0, score))

        # 4. Determine Crisis Level & Routing Protocol
        if risk_score >= 80 or len(vectors) >= 2 or "Health, Hygiene & Safety Violation" in vectors:
            crisis_level = CrisisLevel.CRITICAL
            escalation_target = "Executive Incident Response Team & Regional General Manager"
            sla_window = "< 15 Minutes (Immediate Containment)"
            recommended_action = "Initiate private direct outreach by Store GM, inspect hygiene/batch logs, log internal incident ticket, and route to Human Approval before public reply."
        elif risk_score >= 60 or vectors:
            crisis_level = CrisisLevel.HIGH
            escalation_target = "Branch Operations Manager & Quality Assurance Lead"
            sla_window = "< 2 Hours"
            recommended_action = "Send personalized empathetic response with private escalation channel and hold for manager review."
        elif risk_score >= 35 or star_rating <= 2:
            crisis_level = CrisisLevel.MEDIUM
            escalation_target = "Guest Relations Specialist"
            sla_window = "< 6 Hours"
            recommended_action = "Standard service recovery response with invitation to share details privately."
        else:
            crisis_level = CrisisLevel.LOW
            escalation_target = "Automated AI Brand Agent / Customer Support Desk"
            sla_window = "< 24 Hours"
            recommended_action = "Standard appreciative response thanking customer and encouraging return visit."

        if not flag_reasons:
            flag_reasons.append("Routine customer review without critical risk triggers detected.")

        return CrisisEvaluation(
            risk_score=risk_score,
            crisis_level=crisis_level,
            threat_vectors=vectors if vectors else ["Routine Feedback"],
            matched_triggers=matched,
            flag_reasons=flag_reasons,
            escalation_target=escalation_target,
            sla_window=sla_window,
            recommended_action=recommended_action
        )
