"""
Revio 2.0 Multi-Agent Response Generation Engine
Produces persona-aligned, brand-grounded responses with safety guardrails and Human-in-the-Loop workflows.
"""

import hashlib
import random
from typing import Dict, List, Optional
from src.config import BrandPersona, CrisisLevel, FORBIDDEN_PHRASES
from src.analyzer import ReviewAnalysis
from src.crisis_detector import CrisisEvaluation


class GeneratedResponse:
    def __init__(
        self,
        response_text: str,
        persona: BrandPersona,
        ticket_id: Optional[str],
        hitl_status: str,
        hitl_reason: str,
        guardrail_passed: bool,
        actionable_steps: List[str]
    ):
        self.response_text = response_text
        self.persona = persona
        self.ticket_id = ticket_id
        self.hitl_status = hitl_status
        self.hitl_reason = hitl_reason
        self.guardrail_passed = guardrail_passed
        self.actionable_steps = actionable_steps

    def to_dict(self) -> Dict:
        return {
            "response_text": self.response_text,
            "persona": self.persona.value,
            "ticket_id": self.ticket_id,
            "hitl_status": self.hitl_status,
            "hitl_reason": self.hitl_reason,
            "guardrail_passed": self.guardrail_passed,
            "actionable_steps": self.actionable_steps
        }


class ResponseGenerator:
    """Agentic response synthesizer with built-in compliance validator and policy enforcement."""

    def __init__(self, brand_name: str = "Cynbit Hospitality Group"):
        self.brand_name = brand_name

    def _generate_ticket_id(self, customer_name: str, branch_name: str) -> str:
        seed = f"{customer_name}-{branch_name}-{random.randint(1000, 9999)}"
        digest = hashlib.md5(seed.encode()).hexdigest()[:6].upper()
        return f"REV-{digest}"

    def generate(
        self,
        customer_name: str,
        branch_name: str,
        analysis: ReviewAnalysis,
        crisis: CrisisEvaluation,
        persona: BrandPersona = BrandPersona.EMPATHETIC_RESOLUTION
    ) -> GeneratedResponse:
        first_name = customer_name.split()[0] if customer_name else "Valued Guest"
        ticket_id = None
        actionable_steps: List[str] = []

        # Determine negative aspects mentioned
        negative_aspects = [a.category for a in analysis.detected_aspects if a.sentiment.value == "NEGATIVE"]
        positive_aspects = [a.category for a in analysis.detected_aspects if a.sentiment.value == "POSITIVE"]

        # -------------------------------------------------------------
        # Branch 1: Critical & High Crisis Escalation Response
        # -------------------------------------------------------------
        if crisis.crisis_level in [CrisisLevel.CRITICAL, CrisisLevel.HIGH]:
            ticket_id = self._generate_ticket_id(customer_name, branch_name)
            actionable_steps = [
                f"Escalation ticket {ticket_id} automatically dispatched to General Manager of {branch_name}",
                "Review withheld from public auto-reply; pending human lead approval",
                "Flagged for mandatory customer direct telephone outreach within 15 minutes"
            ]

            if persona == BrandPersona.EXECUTIVE_ESCALATION or crisis.crisis_level == CrisisLevel.CRITICAL:
                response_text = (
                    f"Dear {first_name}, thank you for bringing this matter immediately to our attention. "
                    f"We treat feedback regarding {', '.join(crisis.threat_vectors)} with the utmost priority and urgency. "
                    f"This situation does not reflect our operating standards at {branch_name}.\n\n"
                    f"We have opened priority internal incident case #{ticket_id}. Our General Manager and executive leadership team "
                    f"have been notified and are actively reviewing this incident. Please connect with us directly at "
                    f"executive-care@cynbit.in or call our direct escalation line at +91-89479-62667 so we can address your experience immediately and thoroughly."
                )
            else:
                response_text = (
                    f"Hello {first_name}, we are deeply concerned to read your review regarding your recent visit to {branch_name}. "
                    f"The issues you experienced with {', '.join(negative_aspects) if negative_aspects else 'our service'} are completely unacceptable to us.\n\n"
                    f"We have registered formal ticket #{ticket_id} with our senior operations team to investigate this immediately. "
                    f"We would welcome the opportunity to speak with you directly to make this right. Please email us at care@cynbit.in "
                    f"or call +91-89479-62667 with your ticket number #{ticket_id}."
                )

            hitl_status = "REQUIRES_HUMAN_REVIEW"
            hitl_reason = f"Urgency Score {crisis.risk_score}% ({crisis.crisis_level.value}) — Threat Vectors: {', '.join(crisis.threat_vectors)}"

        # -------------------------------------------------------------
        # Branch 2: Moderate Negative / Mixed Experience Response
        # -------------------------------------------------------------
        elif analysis.star_rating <= 2 or analysis.overall_sentiment.value in ["NEGATIVE", "MIXED"]:
            ticket_id = self._generate_ticket_id(customer_name, branch_name)
            actionable_steps = [
                f"Generated resolution tracking case #{ticket_id}",
                f"Internal alert sent to {branch_name} Guest Relations team",
                "Service recovery voucher queue recommended"
            ]

            aspect_focus = f"regarding {', '.join(negative_aspects)}" if negative_aspects else ""

            if persona == BrandPersona.FORMAL_ENTERPRISE:
                response_text = (
                    f"Dear {first_name},\n\nThank you for sharing your candid review regarding your visit to {branch_name}. "
                    f"We regret that your experience {aspect_focus} did not meet expectations.\n\n"
                    f"We hold our teams to rigorous quality standards and have forwarded your feedback to branch management under case #{ticket_id}. "
                    f"Should you wish to discuss your experience further, our guest relations desk is available at support@cynbit.in."
                )
            elif persona == BrandPersona.WARM_CONCILIATORY:
                response_text = (
                    f"Hi {first_name}, thank you for your honest feedback. We're truly sorry that your visit to {branch_name} "
                    f"fell short of what you deserved, especially {aspect_focus}.\n\n"
                    f"Your experience matters immensely to our whole team. We've logged this as inquiry #{ticket_id} with our branch supervisor. "
                    f"We would love the chance to make it up to you on your next visit. Please drop us a note at care@cynbit.in."
                )
            else:  # Empathetic Resolution
                response_text = (
                    f"Hello {first_name}, thank you for reaching out to us. We are genuinely sorry to hear about your experience at {branch_name}. "
                    f"We take concerns regarding {', '.join(negative_aspects) if negative_aspects else 'service quality'} very seriously.\n\n"
                    f"We have documented this feedback under reference #{ticket_id} for our branch manager to review and take corrective action with the team. "
                    f"Please contact us at care@cynbit.in so we can learn more and ensure your next visit is seamless."
                )

            hitl_status = "REQUIRES_HUMAN_REVIEW" if analysis.star_rating == 1 else "AUTO_APPROVED"
            hitl_reason = "Low rating requires QA review" if analysis.star_rating == 1 else "Standard service recovery protocol"

        # -------------------------------------------------------------
        # Branch 3: Positive & Delight Response
        # -------------------------------------------------------------
        else:
            actionable_steps = [
                f"Automated brand advocacy response prepared for {branch_name}",
                "Customer profile marked as Brand Advocate in Revio CRM",
                "Staff recognition flag sent to branch shift manager"
            ]

            highlights = f"especially your kind words on our {', '.join(positive_aspects)}" if positive_aspects else ""

            if persona == BrandPersona.FORMAL_ENTERPRISE:
                response_text = (
                    f"Dear {first_name},\n\nThank you for your generous 5-star rating of {branch_name}. "
                    f"We are delighted to learn that your visit was a pleasant one {highlights}.\n\n"
                    f"We look forward to serving you again in the near future."
                )
            elif persona == BrandPersona.WARM_CONCILIATORY or persona == BrandPersona.EMPATHETIC_RESOLUTION:
                response_text = (
                    f"Hi {first_name}! Thank you so much for the glowing review and 5-star rating! "
                    f"Our team at {branch_name} is thrilled to know you had such a wonderful time {highlights}.\n\n"
                    f"Your support means the world to our kitchen and floor staff. We can't wait to welcome you back again soon!"
                )
            else:
                response_text = (
                    f"Hello {first_name}, thank you for taking the time to share your delightful experience at {branch_name}. "
                    f"We are committed to delivering memorable visits, and we're so glad our team exceeded your expectations.\n\n"
                    f"See you again soon!"
                )

            hitl_status = "AUTO_APPROVED"
            hitl_reason = "Positive review with zero crisis markers; eligible for instant publishing"

        # -------------------------------------------------------------
        # Guardrail Verification
        # -------------------------------------------------------------
        lower_resp = response_text.lower()
        guardrail_passed = True
        for phrase in FORBIDDEN_PHRASES:
            if phrase in lower_resp:
                guardrail_passed = False
                response_text = response_text.replace(phrase, "[PROTECTED_RESOLUTION_CLAUSE]")

        return GeneratedResponse(
            response_text=response_text,
            persona=persona,
            ticket_id=ticket_id,
            hitl_status=hitl_status,
            hitl_reason=hitl_reason,
            guardrail_passed=guardrail_passed,
            actionable_steps=actionable_steps
        )
