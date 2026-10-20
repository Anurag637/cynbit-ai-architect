"""
Revio 2.0 Production REST API
FastAPI microservice implementation for Cynbit's AI reputation architecture.
"""

from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from src.analyzer import AspectSentimentAnalyzer
from src.crisis_detector import CrisisDetector
from src.response_generator import ResponseGenerator
from src.analytics import EnterpriseAnalyticsEngine
from src.data_generator import load_dataset
from src.config import BrandPersona


app = FastAPI(
    title="Revio 2.0 AI Reputation Intelligence API",
    description="Enterprise API for Aspect-Based Sentiment Analysis, Crisis Escalation, and Brand-Governed Responses.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Service Instances
analyzer = AspectSentimentAnalyzer()
crisis_detector = CrisisDetector()
response_generator = ResponseGenerator()
analytics_engine = EnterpriseAnalyticsEngine()


# -----------------------------------------------------------------------------
# Pydantic Schemas
# -----------------------------------------------------------------------------
class ReviewInput(BaseModel):
    review_text: str = Field(..., min_length=5, description="Full customer review text")
    star_rating: int = Field(3, ge=1, le=5, description="Review star rating from 1 to 5")
    customer_name: Optional[str] = Field("Guest", description="Name of the customer")
    branch_name: Optional[str] = Field("Jaipur Flagship", description="Branch/Location name")


class ResponseRequest(BaseModel):
    review_text: str = Field(..., min_length=5)
    star_rating: int = Field(3, ge=1, le=5)
    customer_name: str = "Valued Guest"
    branch_name: str = "Cynbit Branch"
    persona: str = Field(BrandPersona.EMPATHETIC_RESOLUTION.value, description="Brand voice persona")


class BatchReviewInput(BaseModel):
    reviews: List[ReviewInput]


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {
        "service": "Revio 2.0 AI Reputation Intelligence Engine",
        "company": "Cynbit Technologies Private Limited",
        "status": "online",
        "docs_url": "/docs",
        "version": "2.0.0"
    }


@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy",
        "engine": "active",
        "absa_taxonomy_aspects": 6,
        "crisis_rules_loaded": True
    }


@app.post("/api/v1/analyze")
def analyze_review(data: ReviewInput):
    """Performs Aspect-Based Sentiment Analysis and Crisis Risk Scoring on a single review."""
    analysis = analyzer.analyze(data.review_text, data.star_rating)
    crisis = crisis_detector.evaluate(data.review_text, data.star_rating)

    return {
        "review_text": data.review_text,
        "star_rating": data.star_rating,
        "analysis": analysis.to_dict(),
        "crisis_evaluation": crisis.to_dict()
    }


@app.post("/api/v1/respond")
def generate_response(data: ResponseRequest):
    """Synthesizes a brand-grounded response with safety guardrails and Human-in-the-Loop triage."""
    try:
        persona = BrandPersona(data.persona)
    except ValueError:
        persona = BrandPersona.EMPATHETIC_RESOLUTION

    analysis = analyzer.analyze(data.review_text, data.star_rating)
    crisis = crisis_detector.evaluate(data.review_text, data.star_rating)
    response = response_generator.generate(
        customer_name=data.customer_name,
        branch_name=data.branch_name,
        analysis=analysis,
        crisis=crisis,
        persona=persona
    )

    return {
        "customer_name": data.customer_name,
        "branch_name": data.branch_name,
        "analysis_summary": {
            "overall_sentiment": analysis.overall_sentiment.value,
            "crisis_level": crisis.crisis_level.value,
            "risk_score": crisis.risk_score
        },
        "response": response.to_dict()
    }


@app.post("/api/v1/batch-analyze")
def batch_analyze(data: BatchReviewInput):
    """Enriches a batch of reviews with aspect sentiment and crisis metadata."""
    raw_list = [
        {
            "id": f"REV-REQ-{idx+1}",
            "review_text": r.review_text,
            "star_rating": r.star_rating,
            "customer_name": r.customer_name or "Guest",
            "branch_name": r.branch_name or "General",
            "platform": "API"
        }
        for idx, r in enumerate(data.reviews)
    ]
    enriched = analytics_engine.process_reviews(raw_list)
    summary = analytics_engine.generate_executive_summary(enriched)
    return {
        "count": len(enriched),
        "executive_summary": summary,
        "enriched_reviews": enriched
    }


@app.get("/api/v1/analytics/summary")
def get_analytics_summary():
    """Returns pre-aggregated enterprise KPIs for the benchmark dataset."""
    reviews = load_dataset()
    enriched = analytics_engine.process_reviews(reviews)
    summary = analytics_engine.generate_executive_summary(enriched)
    return summary


@app.get("/api/v1/reviews")
def get_reviews(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    """Returns paginated reviews from the benchmark dataset with real-time NLP enrichment."""
    reviews = load_dataset()
    sliced = reviews[offset: offset + limit]
    enriched = analytics_engine.process_reviews(sliced)
    return {
        "total": len(reviews),
        "limit": limit,
        "offset": offset,
        "reviews": enriched
    }
