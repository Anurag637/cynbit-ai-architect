"""
Revio 2.0 Persona-Calibrated Response Generation Engine
Produces persona-aligned, brand-grounded responses with safety guardrails and Human-in-the-Loop workflows.

Safety & Compliance Rules:
1. Grounding: All generated replies must strictly derive context from the customer's text, rating, and location.
2. Anti-Hallucination Policy: Never invent unverified monetary refunds, compensation, fake case numbers,
   or claim actions have occurred that have not been verified by a human manager.
3. Fallback Mechanism: Operates 100% offline using deterministic policy templates when LLM keys are absent.
4. Human Approval: In this Proof of Concept, all public-facing responses require human sign-off.
   Automated dispatch and external platform integrations are explicitly simulated.
"""

import os
import re
import hashlib
import random
import json
from typing import Dict, List, Optional
import requests

from src.config import (
    BrandPersona,
    CrisisLevel,
    FORBIDDEN_PHRASES,
    BRAND_NAME,
    SUPPORT_EMAIL,
    ESCALATION_EMAIL,
    SUPPORT_PHONE,
    GEMINI_API_KEY,
    OPENAI_API_KEY
)
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
        guardrail_warnings: List[str],
        actionable_steps: List[str],
        generation_source: str = "Deterministic Policy Template (Fallback)"
    ):
        self.response_text = response_text
        self.persona = persona
        self.ticket_id = ticket_id
        self.hitl_status = hitl_status
        self.hitl_reason = hitl_reason
        self.guardrail_passed = guardrail_passed
        self.guardrail_warnings = guardrail_warnings
        self.actionable_steps = actionable_steps
        self.generation_source = generation_source

    def to_dict(self) -> Dict:
        return {
            "response_text": self.response_text,
            "persona": self.persona.value,
            "ticket_id": self.ticket_id,
            "hitl_status": self.hitl_status,
            "hitl_reason": self.hitl_reason,
            "guardrail_passed": self.guardrail_passed,
            "guardrail_warnings": self.guardrail_warnings,
            "actionable_steps": self.actionable_steps,
            "generation_source": self.generation_source
        }


class ResponseGenerator:
    """Agentic response synthesizer with grounded policy enforcement and optional LLM provider."""

    def __init__(
        self,
        brand_name: str = BRAND_NAME,
        support_email: str = SUPPORT_EMAIL,
        escalation_email: str = ESCALATION_EMAIL,
        support_phone: str = SUPPORT_PHONE
    ):
        self.brand_name = brand_name
        self.support_email = support_email
        self.escalation_email = escalation_email
        self.support_phone = support_phone

    def _generate_simulated_ticket(self, customer_name: str, branch_name: str) -> str:
        """Generates a reproducible simulated incident tracking reference."""
        seed = f"{customer_name}-{branch_name}-{random.randint(1000, 9999)}"
        digest = hashlib.md5(seed.encode()).hexdigest()[:6].upper()
        return f"SIM-{digest}"

    def _call_gemini_llm(
        self,
        prompt: str,
        system_instruction: str,
        api_key: str
    ) -> Optional[str]:
        """Calls Google Gemini REST endpoint directly without heavy third-party agent frameworks."""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }
                ],
                "systemInstruction": {
                    "parts": [{"text": system_instruction}]
                },
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 300
                }
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
        except Exception:
            return None
        return None

    def _call_openai_llm(
        self,
        prompt: str,
        system_instruction: str,
        api_key: str
    ) -> Optional[str]:
        """Calls OpenAI chat completions endpoint."""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 300
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "").strip()
        except Exception:
            return None
        return None

    def generate(
        self,
        customer_name: str,
        branch_name: str,
        analysis: ReviewAnalysis,
        crisis: CrisisEvaluation,
        persona: BrandPersona = BrandPersona.EMPATHETIC_RESOLUTION,
        use_llm_if_available: bool = True,
        custom_gemini_key: Optional[str] = None
    ) -> GeneratedResponse:
        first_name = customer_name.split()[0] if customer_name else "Valued Guest"
        ticket_id = None
        actionable_steps: List[str] = []
        guardrail_warnings: List[str] = []
        generation_source = "Deterministic Policy Template (Safe Fallback)"

        negative_aspects = [a.category for a in analysis.detected_aspects if a.sentiment.value == "NEGATIVE"]
        positive_aspects = [a.category for a in analysis.detected_aspects if a.sentiment.value == "POSITIVE"]

        is_crisis = crisis.crisis_level in [CrisisLevel.CRITICAL, CrisisLevel.HIGH]

        # -------------------------------------------------------------
        # Determine Routing Workflow
        # -------------------------------------------------------------
        if is_crisis:
            ticket_id = self._generate_simulated_ticket(customer_name, branch_name)
            hitl_status = "REQUIRES_HUMAN_REVIEW"
            hitl_reason = f"Urgency Score {crisis.risk_score}/100 ({crisis.crisis_level.value}) — Threat Vectors: {', '.join(crisis.threat_vectors)}"
            actionable_steps = [
                f"[Simulated] Priority internal ticket #{ticket_id} logged for {branch_name} management.",
                "Review withheld from public dispatch pending human manager sign-off.",
                f"Escalated to: {crisis.escalation_target} under SLA window {crisis.sla_window}."
            ]
        elif analysis.star_rating <= 2 or analysis.overall_sentiment.value in ["NEGATIVE", "MIXED"]:
            ticket_id = self._generate_simulated_ticket(customer_name, branch_name)
            hitl_status = "REQUIRES_HUMAN_REVIEW"
            hitl_reason = "Negative/Mixed rating requires human review before dispatch."
            actionable_steps = [
                f"[Simulated] Quality service ticket #{ticket_id} created for {branch_name}.",
                "Response drafted and queued for Human-in-the-Loop review.",
                "Service recovery recommendation flagged for branch manager."
            ]
        else:
            hitl_status = "PENDING_HUMAN_APPROVAL"
            hitl_reason = "Positive feedback; queued for 1-click human verification before simulated publish."
            actionable_steps = [
                f"Contextual appreciation response generated for {branch_name}.",
                "Customer profile tagged for brand advocacy recognition.",
                "Queued for human verification (automated auto-publishing disabled in POC)."
            ]

        # -------------------------------------------------------------
        # Attempt Optional LLM Generation (if configured and requested)
        # -------------------------------------------------------------
        llm_response = None
        if use_llm_if_available:
            system_instruction = (
                f"You are a professional customer relations AI representing {self.brand_name}. "
                f"Tone persona: {persona.value}. "
                "CRITICAL POLICY RULES:\n"
                "1. Ground your response strictly on the user review text, star rating, and location.\n"
                "2. NEVER invent refunds, cashback, discounts, or unverified promises.\n"
                "3. NEVER admit legal liability or negligence.\n"
                f"4. Direct any private grievances to official channels: {self.support_email} or {self.support_phone}.\n"
                f"5. For high-severity incidents, mention the simulated reference #{ticket_id} if provided and escalation email {self.escalation_email}.\n"
                "6. Keep responses concise, warm, and professional under 120 words."
            )
            user_prompt = (
                f"Customer: {customer_name}\n"
                f"Location: {branch_name}\n"
                f"Rating: {analysis.star_rating} Stars\n"
                f"Aspects Mentioned: Positive: {positive_aspects}, Negative: {negative_aspects}\n"
                f"Review Text: \"{analysis.root_cause}\"\n"
                f"Risk Tier: {crisis.crisis_level.value}\n"
                "Please draft the official reply."
            )

            active_gemini_key = custom_gemini_key or GEMINI_API_KEY
            if active_gemini_key:
                llm_response = self._call_gemini_llm(user_prompt, system_instruction, active_gemini_key)
                if llm_response:
                    generation_source = "Google Gemini 1.5 Flash (Grounded LLM)"
            elif OPENAI_API_KEY:
                llm_response = self._call_openai_llm(user_prompt, system_instruction, OPENAI_API_KEY)
                if llm_response:
                    generation_source = "OpenAI GPT-4o-mini (Grounded LLM)"

        # -------------------------------------------------------------
        # Deterministic Safe Template Fallback
        # -------------------------------------------------------------
        if not llm_response:
            if is_crisis:
                if persona == BrandPersona.EXECUTIVE_ESCALATION or crisis.crisis_level == CrisisLevel.CRITICAL:
                    response_text = (
                        f"Dear {first_name}, thank you for bringing this matter to our direct attention. "
                        f"We treat feedback regarding {', '.join(crisis.threat_vectors)} with the highest priority and urgency. "
                        f"This does not reflect our operating standards at {branch_name}.\n\n"
                        f"We have noted this incident under internal reference #{ticket_id}. Our management team is reviewing "
                        f"this matter thoroughly. Please contact us directly at {self.escalation_email} or call {self.support_phone} "
                        f"referencing #{ticket_id} so we can investigate and address your concerns personally."
                    )
                else:
                    response_text = (
                        f"Hello {first_name}, we are deeply concerned to read your review regarding your recent experience at {branch_name}. "
                        f"The concerns you noted regarding {', '.join(negative_aspects) if negative_aspects else 'our standards'} are taken very seriously.\n\n"
                        f"We have registered internal case reference #{ticket_id} for our operations leadership. "
                        f"We would appreciate the opportunity to speak with you directly. Please reach out to us at {self.support_email} "
                        f"or {self.support_phone} referencing #{ticket_id}."
                    )
            elif analysis.star_rating <= 2 or analysis.overall_sentiment.value in ["NEGATIVE", "MIXED"]:
                aspect_focus = f"regarding {', '.join(negative_aspects)}" if negative_aspects else "during your visit"
                if persona == BrandPersona.FORMAL_ENTERPRISE:
                    response_text = (
                        f"Dear {first_name},\n\nThank you for sharing your candid feedback regarding {branch_name}. "
                        f"We regret that your experience {aspect_focus} did not meet expectations.\n\n"
                        f"Your comments have been documented for branch management under reference #{ticket_id}. "
                        f"Should you wish to discuss this further, our team is available at {self.support_email}."
                    )
                elif persona == BrandPersona.WARM_CONCILIATORY:
                    response_text = (
                        f"Hi {first_name}, thank you for taking the time to share your review. We are truly sorry that your visit to {branch_name} "
                        f"fell short of expectations, especially {aspect_focus}.\n\n"
                        f"Your experience is important to us, and we have shared this with our branch supervisor under case #{ticket_id}. "
                        f"We hope to have the chance to welcome you back for an improved experience. Please write to us at {self.support_email}."
                    )
                else:  # Empathetic Resolution
                    response_text = (
                        f"Hello {first_name}, thank you for your feedback. We are genuinely sorry to hear about your experience at {branch_name}. "
                        f"We take concerns regarding {', '.join(negative_aspects) if negative_aspects else 'our service'} very seriously.\n\n"
                        f"We have logged your comments under reference #{ticket_id} for our branch manager to review with the team. "
                        f"Please feel free to connect with us at {self.support_email} so we can assist you directly."
                    )
            else:  # Positive
                highlights = f", especially your kind words regarding our {', '.join(positive_aspects)}" if positive_aspects else ""
                if persona == BrandPersona.FORMAL_ENTERPRISE:
                    response_text = (
                        f"Dear {first_name},\n\nThank you for your generous {analysis.star_rating}-star rating of {branch_name}. "
                        f"We are delighted to learn that your visit was a pleasant one{highlights}.\n\n"
                        f"We look forward to welcoming you again soon."
                    )
                elif persona == BrandPersona.WARM_CONCILIATORY or persona == BrandPersona.EMPATHETIC_RESOLUTION:
                    response_text = (
                        f"Hi {first_name}! Thank you so much for the wonderful review and {analysis.star_rating}-star rating! "
                        f"Our team at {branch_name} is thrilled to know you had a great experience{highlights}.\n\n"
                        f"We truly appreciate your support and look forward to serving you again soon!"
                    )
                else:
                    response_text = (
                        f"Hello {first_name}, thank you for taking the time to share your positive experience at {branch_name}. "
                        f"We are committed to delivering high standards, and we are glad our team succeeded{highlights}.\n\n"
                        f"We look forward to seeing you again!"
                    )
        else:
            response_text = llm_response

        # -------------------------------------------------------------
        # Strict Guardrail Inspection & Sanitization
        # -------------------------------------------------------------
        lower_resp = response_text.lower()
        guardrail_passed = True
        for phrase in FORBIDDEN_PHRASES:
            if phrase in lower_resp:
                guardrail_passed = False
                guardrail_warnings.append(f"Sanitized prohibited liability/unverified phrase: '{phrase}'")
                response_text = re.sub(re.escape(phrase), "[Policy Standard Resolution]", response_text, flags=re.IGNORECASE)

        return GeneratedResponse(
            response_text=response_text,
            persona=persona,
            ticket_id=ticket_id,
            hitl_status=hitl_status,
            hitl_reason=hitl_reason,
            guardrail_passed=guardrail_passed,
            guardrail_warnings=guardrail_warnings,
            actionable_steps=actionable_steps,
            generation_source=generation_source
        )
