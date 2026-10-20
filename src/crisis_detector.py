"""
Revio 2.0 Crisis Detection & Urgency Triage Engine
Evaluates legal liabilities, health & safety violations, and viral PR threats.
"""

import re
from typing import Dict, List, Tuple
from src.config import CRISIS_TRIGGERS, CrisisLevel


class CrisisEvaluation:
    def __init__(
        self,
        risk_score: int,
        crisis_level: CrisisLevel,
        threat_vectors: List[str],
        matched_triggers: List[str],
        escalation_target: str,
        sla_window: str,
        recommended_action: str
    ):
        self.risk_score = risk_score
        self.crisis_level = crisis_level
        self.threat_vectors = threat_vectors
        self.matched_triggers = matched_triggers
        self.escalation_target = escalation_target
        self.sla_window = sla_window
        self.recommended_action = recommended_action

    def to_dict(self) -> Dict:
        return {
            "risk_score": self.risk_score,
            "crisis_level": self.crisis_level.value,
            "threat_vectors": self.threat_vectors,
            "matched_triggers": self.matched_triggers,
            "escalation_target": self.escalation_target,
            "sla_window": self.sla_window,
            "recommended_action": self.recommended_action
        }


class CrisisDetector:
    """Enterprise risk scoring engine with deterministic rule weights and threat vector clustering."""

    def __init__(self):
        self.triggers = CRISIS_TRIGGERS

    def evaluate(self, text: str, star_rating: int = 3) -> CrisisEvaluation:
        lower_text = text.lower()
        score = 0
        matched: List[str] = []
        vectors: List[str] = []

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

        # 3. Categorize threat vectors
        legal_kws = ["lawyer", "legal action", "sue", "lawsuit", "court", "consumer court", "police", "fir"]
        health_kws = ["food poisoning", "vomiting", "hospital", "sick", "illness", "cockroach", "rat", "maggot", "contaminated"]
        fraud_kws = ["fraud", "scam", "cheating", "stole", "theft", "unauthorized charge"]
        abuse_kws = ["harassment", "assault", "discriminate", "racist", "casteist", "abuse", "threatened"]
        viral_kws = ["twitter", "viral", "instagram", "post online", "municipal", "media", "news"]

        if any(re.search(r'\b' + re.escape(k) + r'\b', lower_text) for k in legal_kws):
            vectors.append("Legal & Regulatory Action")
        if any(re.search(r'\b' + re.escape(k) + r'\b', lower_text) for k in health_kws):
            vectors.append("Health, Hygiene & Safety Violation")
        if any(re.search(r'\b' + re.escape(k) + r'\b', lower_text) for k in fraud_kws):
            vectors.append("Financial Integrity & Fraud Allegation")
        if any(re.search(r'\b' + re.escape(k) + r'\b', lower_text) for k in abuse_kws):
            vectors.append("Harassment & Human Safety")
        if any(re.search(r'\b' + re.escape(k) + r'\b', lower_text) for k in viral_kws):
            vectors.append("Public Viral PR Exposure")

        # Cap score between 0 and 100
        risk_score = min(100, max(0, score))

        # 4. Determine Crisis Level & Routing Protocol
        if risk_score >= 80 or len(vectors) >= 2 or "Health, Hygiene & Safety Violation" in vectors:
            crisis_level = CrisisLevel.CRITICAL
            escalation_target = "Executive Incident Response Team & Regional General Manager"
            sla_window = "< 15 Minutes (Immediate Containment)"
            recommended_action = "Initiate private direct call by Store GM, freeze affected station/batch, issue formal dispute incident ticket, and halt automated public post."
        elif risk_score >= 60 or vectors:
            crisis_level = CrisisLevel.HIGH
            escalation_target = "Branch Operations Manager & Quality Assurance Lead"
            sla_window = "< 2 Hours"
            recommended_action = "Send personalized empathetic response with dedicated resolution ticket ID and private escalation phone line."
        elif risk_score >= 35 or star_rating <= 2:
            crisis_level = CrisisLevel.MEDIUM
            escalation_target = "Guest Relations Specialist"
            sla_window = "< 6 Hours"
            recommended_action = "Standard service recovery message with feedback invitation and retention voucher."
        else:
            crisis_level = CrisisLevel.LOW
            escalation_target = "Automated AI Brand Agent"
            sla_window = "< 24 Hours"
            recommended_action = "Deploy appreciative brand response with loyalty reinforcement."

        return CrisisEvaluation(
            risk_score=risk_score,
            crisis_level=crisis_level,
            threat_vectors=vectors if vectors else ["Routine Feedback"],
            matched_triggers=matched,
            escalation_target=escalation_target,
            sla_window=sla_window,
            recommended_action=recommended_action
        )
