"""
Revio 2.0 Multi-Location Enterprise Analytics Module
Computes branch rankings, aspect health indices, crisis incidence rates, and root cause distributions.
"""

from typing import Dict, List, Any
import pandas as pd
from src.analyzer import AspectSentimentAnalyzer
from src.crisis_detector import CrisisDetector
from src.config import ASPECT_CATEGORIES


class EnterpriseAnalyticsEngine:
    """Aggregates review signals across distributed brand locations."""

    def __init__(self):
        self.analyzer = AspectSentimentAnalyzer()
        self.crisis_detector = CrisisDetector()

    def process_reviews(self, raw_reviews: List[Dict]) -> List[Dict]:
        """Enriches raw reviews with NLP sentiment and crisis metadata."""
        enriched = []
        for r in raw_reviews:
            analysis = self.analyzer.analyze(r["review_text"], r.get("star_rating", 3))
            crisis = self.crisis_detector.evaluate(r["review_text"], r.get("star_rating", 3))

            enriched.append({
                **r,
                "overall_sentiment": analysis.overall_sentiment.value,
                "compound_score": analysis.compound_score,
                "primary_emotion": analysis.primary_emotion,
                "root_cause": analysis.root_cause,
                "aspects": [a.to_dict() for a in analysis.detected_aspects],
                "risk_score": crisis.risk_score,
                "crisis_level": crisis.crisis_level.value,
                "threat_vectors": crisis.threat_vectors,
                "escalation_target": crisis.escalation_target,
                "sla_window": crisis.sla_window,
                "is_crisis": crisis.crisis_level.value in ["HIGH", "CRITICAL"]
            })
        return enriched

    def generate_executive_summary(self, enriched_reviews: List[Dict]) -> Dict[str, Any]:
        """Calculates global enterprise KPIs across all branches."""
        if not enriched_reviews:
            return {}

        df = pd.DataFrame(enriched_reviews)
        total_reviews = len(df)
        avg_rating = float(df["star_rating"].mean())
        avg_sentiment = float(df["compound_score"].mean())

        crisis_count = int(df["is_crisis"].sum())
        crisis_pct = round((crisis_count / total_reviews) * 100, 1)

        # Sentiment counts
        sentiment_counts = df["overall_sentiment"].value_counts().to_dict()

        # Platform counts
        platform_counts = df["platform"].value_counts().to_dict()

        # Aspect Health Aggregation
        aspect_scores: Dict[str, List[float]] = {k: [] for k in ASPECT_CATEGORIES.keys()}
        aspect_pos_neg: Dict[str, Dict[str, int]] = {k: {"pos": 0, "neg": 0, "neu": 0} for k in ASPECT_CATEGORIES.keys()}

        for r in enriched_reviews:
            for asp in r.get("aspects", []):
                cat = asp["category"]
                if cat in aspect_scores:
                    aspect_scores[cat].append(asp["score"])
                    if asp["sentiment"] == "POSITIVE":
                        aspect_pos_neg[cat]["pos"] += 1
                    elif asp["sentiment"] == "NEGATIVE":
                        aspect_pos_neg[cat]["neg"] += 1
                    else:
                        aspect_pos_neg[cat]["neu"] += 1

        aspect_health = {}
        for cat, scores in aspect_scores.items():
            aspect_health[cat] = {
                "avg_score": round(sum(scores) / len(scores), 2) if scores else 0.0,
                "mentions": len(scores),
                "positive": aspect_pos_neg[cat]["pos"],
                "negative": aspect_pos_neg[cat]["neg"],
                "neutral": aspect_pos_neg[cat]["neu"]
            }

        # Branch breakdown
        branch_summary = []
        for branch_name, group in df.groupby("branch_name"):
            branch_crises = int(group["is_crisis"].sum())
            branch_summary.append({
                "branch_name": branch_name,
                "city": group["branch_city"].iloc[0] if "branch_city" in group.columns else "Unknown",
                "total_reviews": len(group),
                "avg_rating": round(float(group["star_rating"].mean()), 2),
                "avg_sentiment": round(float(group["compound_score"].mean()), 2),
                "crisis_count": branch_crises,
                "crisis_rate_pct": round((branch_crises / len(group)) * 100, 1)
            })

        # Rank branches by health
        branch_summary.sort(key=lambda x: (x["avg_rating"], x["avg_sentiment"]), reverse=True)

        return {
            "total_reviews": total_reviews,
            "avg_rating": round(avg_rating, 2),
            "avg_sentiment": round(avg_sentiment, 2),
            "crisis_count": crisis_count,
            "crisis_pct": crisis_pct,
            "sentiment_distribution": sentiment_counts,
            "platform_distribution": platform_counts,
            "aspect_health": aspect_health,
            "branch_rankings": branch_summary
        }
