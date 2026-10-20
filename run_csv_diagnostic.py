"""
Diagnostics Runner for Both Test CSV Files
"""

import pandas as pd
from src.ingestion import validate_and_parse_dataframe
from src.analytics import EnterpriseAnalyticsEngine

analytics = EnterpriseAnalyticsEngine()

print("=" * 75)
print("  DIAGNOSTIC TEST REPORT 1: Franchise Batch (data/test_reviews_franchise_batch.csv)")
print("=" * 75)
df1 = pd.read_csv("data/test_reviews_franchise_batch.csv")
records1, meta1 = validate_and_parse_dataframe(df1)
print(f"Ingestion Status : Received={meta1['total_rows_received']}, Retained={meta1['valid_rows_retained']}, Dropped={meta1['dropped_rows']}")
enriched1 = analytics.process_reviews(records1)
summary1 = analytics.generate_executive_summary(enriched1)
print(f"Total Reviews    : {summary1['total_reviews']}")
print(f"Average Rating   : {summary1['avg_rating']} / 5.0")
print(f"Polarity Index   : {summary1['avg_sentiment']:+.2f}")
print(f"Crisis Incidence : {summary1['crisis_count']} / {summary1['total_reviews']} ({summary1['crisis_pct']}%)")
print("\nAspect Health Breakdown (Volume & Net Polarity):")
for asp, d in summary1['aspect_health'].items():
    if d['mentions'] > 0:
        print(f"  - {asp:<25}: {d['mentions']} mentions | Net Score: {d['avg_score']:+.2f} (Pos: {d['positive']}, Neg: {d['negative']}, Neu: {d['neutral']})")

print("\nBranch Performance Ranking:")
for b in summary1['branch_rankings']:
    print(f"  - {b['branch_name']} -> {b['total_reviews']} reviews | Rating: {b['avg_rating']} / 5.0 | Net Sentiment: {b['avg_sentiment']:+.2f}")

print("\n" + "=" * 75)
print("  DIAGNOSTIC TEST REPORT 2: Crisis & Edge Cases (data/test_reviews_crisis_and_edge_cases.csv)")
print("=" * 75)
df2 = pd.read_csv("data/test_reviews_crisis_and_edge_cases.csv")
records2, meta2 = validate_and_parse_dataframe(df2)
print(f"Ingestion Status : Received={meta2['total_rows_received']}, Retained={meta2['valid_rows_retained']}, Dropped={meta2['dropped_rows']}")
print("Captured Malformed Validation Errors:")
for err in meta2['sample_errors']:
    print(f"  [X] {err}")

enriched2 = analytics.process_reviews(records2)
summary2 = analytics.generate_executive_summary(enriched2)
print(f"\nTotal Valid Reviews : {summary2['total_reviews']}")
print(f"Average Rating      : {summary2['avg_rating']} / 5.0")
print(f"Crisis Reviews      : {summary2['crisis_count']} / {summary2['total_reviews']} ({summary2['crisis_pct']}%)")

print("\nIntercepted Crisis & High-Risk Reviews:")
for r in enriched2:
    if r['is_crisis']:
        print(f"  [CRISIS ALERT] [{r['id']}] {r['customer_name']} ({r['star_rating']} stars) - {r['branch_name']}")
        print(f"     Review: \"{r['review_text'][:90]}...\"")
        print(f"     Screening Score: {r['risk_score']}/100 ({r['crisis_level']}) | Threat Vectors: {r['threat_vectors']}")
        print(f"     SLA: {r['sla_window']} -> Escalation: {r['escalation_target']}")
        print()
