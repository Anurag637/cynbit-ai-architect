"""
FastAPI Comprehensive Endpoint Audit Script for Revio 2.0
Tests status codes, schemas, validation errors, and response structures using starlette.testclient.
"""

import sys
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("PHASE 10: FASTAPI COMPREHENSIVE ENDPOINT AUDIT")
    print("=" * 60)

    # 1. Root & OpenAPI
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print("[PASS] GET / returned 200 OK")
    assert res.json()["service"] == "Revio 2.0 AI Reputation Intelligence Engine"

    res_docs = client.get("/docs")
    assert res_docs.status_code == 200
    print("[PASS] GET /docs (Swagger UI) returned 200 OK")

    res_openapi = client.get("/openapi.json")
    assert res_openapi.status_code == 200
    print("[PASS] GET /openapi.json returned 200 OK")

    # 2. Health
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "healthy"
    print(f"[PASS] GET /api/v1/health returned 200 OK ({body['status']})")

    # 3. Analyze Valid
    payload = {
        "review_text": "The food was wonderful but the service took over an hour.",
        "star_rating": 2,
        "customer_name": "Test User",
        "branch_name": "Jaipur Flagship"
    }
    res = client.post("/api/v1/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "analysis" in data
    assert "crisis_evaluation" in data
    print(f"[PASS] POST /api/v1/analyze returned 200 OK (Sentiment: {data['analysis']['overall_sentiment']}, Crisis: {data['crisis_evaluation']['crisis_level']})")

    # 4. Analyze Validation: Text too short (< 5 chars)
    bad_payload = {"review_text": "bad", "star_rating": 1}
    res = client.post("/api/v1/analyze", json=bad_payload)
    assert res.status_code == 422, f"Expected 422 for text < 5 chars, got {res.status_code}"
    print(f"[PASS] POST /api/v1/analyze rejected short review with HTTP 422 (Pydantic validation)")

    # 5. Analyze Validation: Invalid star rating (> 5)
    bad_rating = {"review_text": "Valid review text here", "star_rating": 10}
    res = client.post("/api/v1/analyze", json=bad_rating)
    assert res.status_code == 422
    print(f"[PASS] POST /api/v1/analyze rejected star_rating=10 with HTTP 422")

    # 6. Analyze Validation: Missing required field
    missing_text = {"star_rating": 3}
    res = client.post("/api/v1/analyze", json=missing_text)
    assert res.status_code == 422
    print(f"[PASS] POST /api/v1/analyze rejected missing review_text with HTTP 422")

    # 7. Respond Endpoint Valid
    resp_payload = {
        "review_text": "The food was delicious and our server Amit was very polite.",
        "star_rating": 5,
        "customer_name": "Rohan Sharma",
        "branch_name": "Jaipur Malviya Nagar Flagship",
        "persona": "Empathetic & Solution-Oriented"
    }
    res = client.post("/api/v1/respond", json=resp_payload)
    assert res.status_code == 200
    resp_data = res.json()
    assert "response" in resp_data
    assert "response_text" in resp_data["response"]
    assert resp_data["response"]["hitl_status"] == "PENDING_HUMAN_APPROVAL"
    print(f"[PASS] POST /api/v1/respond returned 200 OK with draft status: {resp_data['response']['hitl_status']}")

    # 8. Batch Analyze
    batch_payload = {
        "reviews": [
            {"review_text": "Great breakfast and wonderful coffee.", "star_rating": 5},
            {"review_text": "Waited 45 minutes for stale food.", "star_rating": 1}
        ]
    }
    res = client.post("/api/v1/batch-analyze", json=batch_payload)
    assert res.status_code == 200
    batch_data = res.json()
    assert batch_data["count"] == 2
    assert "executive_summary" in batch_data
    print(f"[PASS] POST /api/v1/batch-analyze returned 200 OK for 2 items")

    # 9. Analytics Summary
    res = client.get("/api/v1/analytics/summary")
    assert res.status_code == 200
    summary = res.json()
    assert "total_reviews" in summary
    assert "avg_sentiment" in summary
    print(f"[PASS] GET /api/v1/analytics/summary returned 200 OK (Total: {summary['total_reviews']}, Avg Rating: {summary['avg_rating']})")

    # 10. Reviews Paginated
    res = client.get("/api/v1/reviews?limit=3&offset=0")
    assert res.status_code == 200
    revs = res.json()
    assert len(revs["reviews"]) == 3
    print(f"[PASS] GET /api/v1/reviews?limit=3 returned 200 OK (returned {len(revs['reviews'])} items)")

    print("\nALL FASTAPI ENDPOINTS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
