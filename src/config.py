"""
Revio 2.0 Configuration Module
Contains system constants, aspect taxonomies, crisis rules, and brand voice settings.
"""

from typing import Dict, List, Set
from enum import Enum


class Sentiment(str, Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"
    MIXED = "MIXED"


class CrisisLevel(str, Enum):
    LOW = "LOW"             # Routine review, score 0-35
    MEDIUM = "MEDIUM"       # Moderate dissatisfaction, score 36-65
    HIGH = "HIGH"           # Significant grievance / churn risk, score 66-84
    CRITICAL = "CRITICAL"   # Severe legal, regulatory, health, or viral PR threat, score 85-100


class BrandPersona(str, Enum):
    EMPATHETIC_RESOLUTION = "Empathetic & Solution-Oriented"
    FORMAL_ENTERPRISE = "Formal & Corporate"
    WARM_CONCILIATORY = "Warm & Conciliatory"
    EXECUTIVE_ESCALATION = "Executive Escalation"


# Standard Aspect Taxonomy for Multi-Location Businesses
ASPECT_CATEGORIES: Dict[str, List[str]] = {
    "Customer Service": [
        "staff", "service", "waiter", "manager", "reception", "crew", "employee", 
        "behavior", "rude", "polite", "friendly", "attitude", "unprofessional", "helpful"
    ],
    "Product & Food Quality": [
        "food", "taste", "dish", "meal", "quality", "fresh", "stale", "cold", "delicious",
        "flavor", "portion", "ingredient", "raw", "overcooked", "burnt", "item", "product"
    ],
    "Speed & Turnaround Time": [
        "time", "delay", "slow", "fast", "quick", "wait", "waiting", "hour", "minutes",
        "late", "prompt", "turnaround", "hurry", "queue", "line"
    ],
    "Cleanliness & Ambience": [
        "clean", "dirty", "hygiene", "smell", "restroom", "washroom", "table", "ac",
        "noise", "atmosphere", "ambience", "decor", "messy", "cockroach", "pest", "dusty"
    ],
    "Pricing & Value": [
        "price", "expensive", "cheap", "cost", "value", "worth", "overpriced", "money",
        "affordable", "overcharge", "rip-off", "bill", "charge"
    ],
    "Billing & Transactions": [
        "billing", "receipt", "payment", "card", "upi", "refund", "extra charge",
        "hidden fee", "invoice", "overbilled", "scam"
    ]
}

# Crisis Trigger Keywords and their Risk Weights
CRISIS_TRIGGERS: Dict[str, int] = {
    # Legal & Regulatory (High Risk)
    "lawyer": 40,
    "legal action": 45,
    "sue": 40,
    "lawsuit": 45,
    "court": 35,
    "consumer court": 45,
    "police": 45,
    "fir": 45,
    "complaint to authorities": 40,

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

    # Severe Financial & Fraud (High Risk)
    "fraud": 45,
    "scam": 45,
    "cheating": 35,
    "stole": 40,
    "theft": 40,
    "robbery": 45,
    "unauthorized charge": 40,

    # Discrimination & Abuse (Critical Risk)
    "harassment": 45,
    "assault": 50,
    "discriminate": 45,
    "racist": 45,
    "casteist": 45,
    "abuse": 40,
    "threatened": 45
}

# Brand Guardrails: Forbidden phrases that create enterprise legal liability
FORBIDDEN_PHRASES: Set[str] = {
    "we admit we were at fault",
    "our team made an illegal error",
    "we will pay you to delete this",
    "here is 100% cashback guaranteed",
    "it was our cook's mistake"
}

# Default Mock Locations
DEFAULT_BRANCHES: List[Dict[str, str]] = [
    {"id": "BR-01", "name": "Jaipur Malviya Nagar Flagship", "city": "Jaipur", "state": "Rajasthan"},
    {"id": "BR-02", "name": "Jaipur Pratap Nagar Tech Hub", "city": "Jaipur", "state": "Rajasthan"},
    {"id": "BR-03", "name": "Gurugram CyberCity Premier", "city": "Gurugram", "state": "Haryana"},
    {"id": "BR-04", "name": "Bengaluru Indiranagar Center", "city": "Bengaluru", "state": "Karnataka"},
    {"id": "BR-05", "name": "Mumbai Bandra West Lab", "city": "Mumbai", "state": "Maharashtra"}
]
