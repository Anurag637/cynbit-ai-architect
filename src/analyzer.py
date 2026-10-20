"""
Revio 2.0 Aspect-Based Sentiment Analysis (ABSA) Engine
Extracts granular operational aspects, polarity scores, emotions, and root cause drivers.

Design Philosophy & Baseline Notes:
- Implementation: Deterministic rule-based lexical engine combining aspect-trigger taxonomies,
  contrastive clause splitting, contextual negation inversion, and lexicon polarity matching.
- Rationale: Provides sub-millisecond latency, zero external API costs, deterministic reproducibility,
  and full interpretability for edge deployment in high-throughput review pipelines.
- Known Limitations: Does not detect subtle double-entendre sarcasm, highly metaphorical phrasing,
  or slang outside the configured lexicon without an upstream fine-tuned Transformer (e.g. DeBERTa/BERT).
"""

import re
from typing import Dict, List, Optional
from src.config import ASPECT_CATEGORIES, Sentiment


POSITIVE_LEXICON = {
    "good", "nice", "fine", "correct", "accurate", "fair", "pleased", "happy",
    "delicious", "amazing", "great", "excellent", "best", "exceptional", "friendly",
    "polite", "quick", "fast", "prompt", "clean", "hygienic", "spotless", "loved",
    "awesome", "wonderful", "warm", "helpful", "affordable", "consistent", "superb",
    "generous", "fresh", "crisp", "recommend", "attentive", "relaxing", "pristine",
    "lajawab", "shandar", "badhiya", "tasty", "yummy", "courteous", "perfect", "10/10"
}

NEGATIVE_LEXICON = {
    "bad", "poor", "incorrect", "wrong", "inaccurate", "unfair", "unhappy", "late",
    "rude", "worst", "terrible", "horrible", "awful", "slow", "delay", "cold", "raw",
    "stale", "tasteless", "dirty", "unhygienic", "smell", "expensive", "overpriced",
    "unauthorized", "scam", "fraud", "unacceptable", "ignored", "spilled", "melted",
    "poisoning", "sick", "cockroach", "disappointed", "abusive", "harassed", "leaking",
    "soggy", "confusing", "overcharged", "cheated", "gross", "crashed", "bakwas",
    "battameez", "batameez", "ganda", "kharab", "mehnga", "badbu", "chori", "dhoka"
}

NEGATION_TERMS = {
    "not", "never", "no", "nobody", "without", "hardly", "scarcely", "barely", "neither", "nor", "nahi", "mat", "na"
}

EMOTION_KEYWORDS = {
    "Anger / Outrage": ["abusive", "harassed", "fraud", "scam", "police", "lawyer", "lawsuit", "cheated", "sue", "battameez", "gunda"],
    "Severe Disgust": ["cockroach", "rat", "hair in food", "maggot", "vomiting", "poisoning", "gross", "dirty", "ganda", "badbu", "zehar"],
    "Frustration / Impatience": ["delay", "waiting", "slow", "ignored", "hour", "minutes", "late", "crashed", "deri"],
    "Delight / Enthusiasm": ["amazing", "exceptional", "loved", "superb", "best", "pristine", "10/10", "world-class", "lajawab"],
    "Satisfaction / Gratitude": ["good", "great", "delicious", "fresh", "polite", "clean", "recommend", "helpful", "badhiya"]
}


class AspectResult:
    def __init__(self, category: str, sentiment: Sentiment, score: float, keywords: List[str], context_snippet: str):
        self.category = category
        self.sentiment = sentiment
        self.score = score
        self.keywords = keywords
        self.context_snippet = context_snippet

    def to_dict(self) -> Dict:
        return {
            "category": self.category,
            "sentiment": self.sentiment.value,
            "score": round(self.score, 2),
            "keywords": self.keywords,
            "context_snippet": self.context_snippet
        }


class ReviewAnalysis:
    def __init__(
        self,
        overall_sentiment: Sentiment,
        compound_score: float,
        detected_aspects: List[AspectResult],
        primary_emotion: str,
        root_cause: str,
        star_rating: int,
        word_count: int
    ):
        self.overall_sentiment = overall_sentiment
        self.compound_score = compound_score
        self.detected_aspects = detected_aspects
        self.primary_emotion = primary_emotion
        self.root_cause = root_cause
        self.star_rating = star_rating
        self.word_count = word_count

    def to_dict(self) -> Dict:
        return {
            "overall_sentiment": self.overall_sentiment.value,
            "compound_score": round(self.compound_score, 2),
            "primary_emotion": self.primary_emotion,
            "root_cause": self.root_cause,
            "star_rating": self.star_rating,
            "word_count": self.word_count,
            "aspects": [a.to_dict() for a in self.detected_aspects]
        }


class AspectSentimentAnalyzer:
    """Production ABSA baseline engine with zero external API latency dependency."""

    def __init__(self):
        self.aspect_taxonomy = ASPECT_CATEGORIES

    def _split_into_clauses(self, text: str) -> List[str]:
        """Split on punctuation and contrastive discourse markers."""
        clauses = re.split(r'[.!?;\n]|(?:\b(?:but|however|although|yet|while|though|lekin|par|magar)\b)', text, flags=re.IGNORECASE)
        return [c.strip() for c in clauses if c.strip()]

    def analyze_aspects(self, text: str) -> List[AspectResult]:
        clauses = self._split_into_clauses(text)
        lower_text = text.lower()
        results: List[AspectResult] = []

        for category, triggers in self.aspect_taxonomy.items():
            matched_keywords = [t for t in triggers if re.search(r'\b' + re.escape(t) + r'\b', lower_text)]
            if not matched_keywords:
                continue

            # Locate relevant context clause
            matched_clause = ""
            for clause in clauses:
                clause_lower = clause.lower()
                if any(re.search(r'\b' + re.escape(kw) + r'\b', clause_lower) for kw in matched_keywords):
                    matched_clause = clause
                    break

            if not matched_clause:
                matched_clause = text[:120]

            # Sentiment calculation for the specific aspect clause
            clause_tokens = set(re.findall(r'\b\w+\b', matched_clause.lower()))
            pos_matches = clause_tokens.intersection(POSITIVE_LEXICON)
            neg_matches = clause_tokens.intersection(NEGATIVE_LEXICON)

            # Check for negation words within the clause
            has_negation = any(neg in clause_tokens for neg in NEGATION_TERMS)

            pos_count = len(pos_matches)
            neg_count = len(neg_matches)

            if has_negation:
                # Invert sentiment polarity on negation (e.g. "not clean" -> negative)
                pos_count, neg_count = neg_count, pos_count

            if pos_count > neg_count:
                sentiment = Sentiment.POSITIVE
                score = min(1.0, 0.4 + (pos_count * 0.25))
            elif neg_count > pos_count:
                sentiment = Sentiment.NEGATIVE
                score = max(-1.0, -0.4 - (neg_count * 0.25))
            else:
                sentiment = Sentiment.NEUTRAL
                score = 0.0

            results.append(AspectResult(
                category=category,
                sentiment=sentiment,
                score=score,
                keywords=matched_keywords,
                context_snippet=matched_clause
            ))

        return results

    def detect_emotion(self, text: str) -> str:
        lower_text = text.lower()
        for emotion, keywords in EMOTION_KEYWORDS.items():
            if any(re.search(r'\b' + re.escape(kw) + r'\b', lower_text) for kw in keywords):
                return emotion
        return "Neutral / Informational"

    def identify_root_cause(self, text: str, aspects: List[AspectResult], star_rating: int) -> str:
        negative_aspects = [a for a in aspects if a.sentiment == Sentiment.NEGATIVE]
        if negative_aspects:
            worst = min(negative_aspects, key=lambda a: a.score)
            return f"Negative Friction in {worst.category} (Mentioned: {', '.join(worst.keywords[:2])})"

        positive_aspects = [a for a in aspects if a.sentiment == Sentiment.POSITIVE]
        if positive_aspects:
            best = max(positive_aspects, key=lambda a: a.score)
            return f"Excellence in {best.category} (Mentioned: {', '.join(best.keywords[:2])})"

        if star_rating >= 4:
            return "General Customer Satisfaction"
        elif star_rating <= 2:
            return "General Service Dissatisfaction"
        return "Balanced Experience"

    def analyze(self, text: str, star_rating: int = 3) -> ReviewAnalysis:
        aspects = self.analyze_aspects(text)
        emotion = self.detect_emotion(text)
        words = len(re.findall(r'\b\w+\b', text))

        if aspects:
            compound_score = sum(a.score for a in aspects) / len(aspects)
        else:
            compound_score = (star_rating - 3) / 2.0

        # Adjust score with star rating signal
        rating_normalized = (star_rating - 3) / 2.0
        final_compound = (compound_score * 0.7) + (rating_normalized * 0.3)
        final_compound = max(-1.0, min(1.0, final_compound))

        # Overall sentiment categorization
        has_pos = any(a.sentiment == Sentiment.POSITIVE for a in aspects)
        has_neg = any(a.sentiment == Sentiment.NEGATIVE for a in aspects)

        if has_pos and has_neg:
            overall_sentiment = Sentiment.MIXED
        elif final_compound > 0.15 or star_rating >= 4:
            overall_sentiment = Sentiment.POSITIVE
        elif final_compound < -0.15 or star_rating <= 2:
            overall_sentiment = Sentiment.NEGATIVE
        else:
            overall_sentiment = Sentiment.NEUTRAL

        root_cause = self.identify_root_cause(text, aspects, star_rating)

        return ReviewAnalysis(
            overall_sentiment=overall_sentiment,
            compound_score=final_compound,
            detected_aspects=aspects,
            primary_emotion=emotion,
            root_cause=root_cause,
            star_rating=star_rating,
            word_count=words
        )
