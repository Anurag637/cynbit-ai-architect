"""
Revio 2.0 Configuration Module
Contains system constants, aspect taxonomies, crisis rules, and brand voice settings.
"""

import os
from typing import Dict, List, Set
from enum import Enum
from pathlib import Path
from dotenv import load_dotenv

# Load environment configuration if present
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Configurable Brand & Resolution Policy Settings (read from environment, with safe defaults)
BRAND_NAME: str = os.getenv("BRAND_NAME", "Cynbit Hospitality Group")
SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", "care@cynbit.in")
ESCALATION_EMAIL: str = os.getenv("ESCALATION_EMAIL", "executive-care@cynbit.in")
SUPPORT_PHONE: str = os.getenv("SUPPORT_PHONE", "+91-89479-62667")

def get_gemini_api_key() -> str:
    """Dynamically resolves Google Gemini API key from Streamlit secrets or environment."""
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for k in ["GEMINI_API_KEY", "gemini_api_key", "GOOGLE_API_KEY", "google_api_key", "GEMINI_KEY", "gemini_key"]:
                if k in st.secrets and st.secrets[k]:
                    return str(st.secrets[k]).strip().strip('"\'')
            if "gemini" in st.secrets and isinstance(st.secrets["gemini"], dict):
                for k in ["api_key", "key"]:
                    if k in st.secrets["gemini"] and st.secrets["gemini"][k]:
                        return str(st.secrets["gemini"][k]).strip().strip('"\'')
    except Exception:
        pass
    for k in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_KEY"]:
        v = os.getenv(k)
        if v:
            return v.strip().strip('"\'')
    return ""


def get_huggingface_api_key() -> str:
    """Dynamically resolves Hugging Face API token from Streamlit secrets or environment."""
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for k in ["HUGGINGFACE_API_KEY", "huggingface_api_key", "HF_TOKEN", "hf_token", "HUGGING_FACE_HUB_TOKEN", "hugging_face_hub_token"]:
                if k in st.secrets and st.secrets[k]:
                    return str(st.secrets[k]).strip().strip('"\'')
            if "huggingface" in st.secrets and isinstance(st.secrets["huggingface"], dict):
                for k in ["api_key", "token"]:
                    if k in st.secrets["huggingface"] and st.secrets["huggingface"][k]:
                        return str(st.secrets["huggingface"][k]).strip().strip('"\'')
    except Exception:
        pass
    for k in ["HUGGINGFACE_API_KEY", "HF_TOKEN", "HUGGING_FACE_HUB_TOKEN"]:
        v = os.getenv(k)
        if v:
            return v.strip().strip('"\'')
    return ""


def get_openai_api_key() -> str:
    """Dynamically resolves OpenAI API key from Streamlit secrets or environment."""
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for k in ["OPENAI_API_KEY", "openai_api_key"]:
                if k in st.secrets and st.secrets[k]:
                    return str(st.secrets[k]).strip().strip('"\'')
    except Exception:
        pass
    v = os.getenv("OPENAI_API_KEY")
    return v.strip().strip('"\'') if v else ""


# Optional LLM API Keys (read from environment or Streamlit Cloud secrets)
GEMINI_API_KEY: str = get_gemini_api_key()
OPENAI_API_KEY: str = get_openai_api_key()
HUGGINGFACE_API_KEY: str = get_huggingface_api_key()
HUGGINGFACE_MODEL: str = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-3.1-8B-Instruct")


class Sentiment(str, Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"
    MIXED = "MIXED"


class CrisisLevel(str, Enum):
    """
    Triage risk tier based on heuristic screening estimation.
    NOTE: Risk scores are priority-ranking screening estimates, not calibrated statistical probabilities.
    """
    LOW = "LOW"             # Routine feedback, score 0-35
    MEDIUM = "MEDIUM"       # Moderate dissatisfaction, score 36-59
    HIGH = "HIGH"           # Elevated grievance / risk flag, score 60-79
    CRITICAL = "CRITICAL"   # Severe legal, health, fraud, or safety concern, score 80-100


class BrandPersona(str, Enum):
    EMPATHETIC_RESOLUTION = "Empathetic & Solution-Oriented"
    FORMAL_ENTERPRISE = "Formal & Corporate"
    WARM_CONCILIATORY = "Warm & Conciliatory"
    EXECUTIVE_ESCALATION = "Executive Escalation"


# Standard Aspect Taxonomy for Multi-Location Businesses (including bilingual & Hinglish variations)
ASPECT_CATEGORIES: Dict[str, List[str]] = {
    "Customer Service": [
        "staff", "service", "waiter", "manager", "reception", "crew", "employee", 
        "behavior", "rude", "polite", "friendly", "attitude", "unprofessional", "helpful",
        "battameez", "batameez", "courteous", "hospitality", "attentive"
    ],
    "Product & Food Quality": [
        "food", "taste", "dish", "meal", "quality", "fresh", "stale", "cold", "delicious",
        "flavor", "portion", "ingredient", "raw", "overcooked", "burnt", "item", "product",
        "khana", "swad", "tasty", "yummy", "lajawab", "bakwas"
    ],
    "Speed & Turnaround Time": [
        "time", "delay", "slow", "fast", "quick", "wait", "waiting", "hour", "minutes",
        "late", "prompt", "turnaround", "hurry", "queue", "line", "delivery", "deri", "jaldi"
    ],
    "Cleanliness & Ambience": [
        "clean", "dirty", "hygiene", "smell", "restroom", "washroom", "table", "ac",
        "noise", "atmosphere", "ambience", "decor", "messy", "cockroach", "pest", "dusty",
        "saaf", "ganda", "unhygienic", "badbu"
    ],
    "Pricing & Value": [
        "price", "expensive", "cheap", "cost", "value", "worth", "overpriced", "money",
        "affordable", "overcharge", "rip-off", "bill", "charge", "mehnga", "sasta", "daam"
    ],
    "Billing & Transactions": [
        "billing", "bill", "receipt", "payment", "card", "upi", "refund", "extra charge",
        "hidden fee", "invoice", "overbilled", "scam", "hisab"
    ]
}

# Crisis Trigger Keywords and their Risk Weights (Screening Index)
CRISIS_TRIGGERS: Dict[str, int] = {
    # Legal & Regulatory (High Risk)
    "lawyer": 40,
    "legal action": 45,
    "sue": 40,
    "lawsuit": 45,
    "court": 35,
    "consumer court": 45,
    "consumer forum": 45,
    "police": 45,
    "fir": 45,
    "complaint to authorities": 40,
    "fssai": 45,

    # Health & Safety Violations (Critical Risk)
    "food poisoning": 50,
    "vomiting": 40,
    "hospital": 45,
    "sick": 35,
    "illness": 40,
    "hair in food": 35,
    "cockroach": 45,
    "rat": 45,
    "maggot": 50,
    "expired": 35,
    "contaminated": 45,
    "zehar": 50,
    "poison": 50,
    "infection": 40,
    "allergy": 45,
    "allergic": 45,
    "anaphylaxis": 50,
    "peanut allergy": 50,
    "peanuts": 40,

    # Severe Financial & Fraud (High Risk)
    "fraud": 45,
    "scam": 45,
    "cheating": 35,
    "stole": 40,
    "theft": 40,
    "robbery": 45,
    "unauthorized charge": 40,
    "charged twice": 40,
    "charged my card twice": 45,
    "double charge": 40,
    "double charged": 40,
    "chori": 40,
    "dhoka": 40,
    "thug": 40,

    # Discrimination & Abuse (Critical Risk)
    "harassment": 45,
    "assault": 50,
    "discriminate": 45,
    "racist": 45,
    "casteist": 45,
    "abuse": 40,
    "threatened": 45,
    "gunda": 45,
    "physical": 40
}

# Brand Guardrails: Forbidden phrases that invent concessions, unauthorized refunds, or legal liability
FORBIDDEN_PHRASES: Set[str] = {
    "we admit we were at fault",
    "our team made an illegal error",
    "we will pay you to delete this",
    "here is 100% cashback guaranteed",
    "it was our cook's mistake",
    "we have refunded your full amount",
    "a full refund has already been credited",
    "we have credited your bank account",
    "free food on your next visit",
    "we guarantee 100% compensation"
}

# Default Mock Locations
DEFAULT_BRANCHES: List[Dict[str, str]] = [
    {"id": "BR-01", "name": "Jaipur Malviya Nagar Flagship", "city": "Jaipur", "state": "Rajasthan"},
    {"id": "BR-02", "name": "Jaipur Pratap Nagar Tech Hub", "city": "Jaipur", "state": "Rajasthan"},
    {"id": "BR-03", "name": "Gurugram CyberCity Premier", "city": "Gurugram", "state": "Haryana"},
    {"id": "BR-04", "name": "Bengaluru Indiranagar Center", "city": "Bengaluru", "state": "Karnataka"},
    {"id": "BR-05", "name": "Mumbai Bandra West Lab", "city": "Mumbai", "state": "Maharashtra"}
]
