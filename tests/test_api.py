"""
Unit tests for Revio 2.0 FastAPI Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.api import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "Revio 2.0" in data["service"]


def test_health_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_analyze_endpoint(client):
    payload = {
        "review_text": "The soup was delicious but billing was slow and overcharged.",
        "star_rating": 2,
        "customer_name": "Karan Johar",
        "branch_name": "Mumbai Bandra West"
    }
    res = client.post("/api/v1/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "analysis" in data
    assert "crisis_evaluation" in data
    assert len(data["analysis"]["aspects"]) >= 1


def test_respond_endpoint(client):
    payload = {
        "review_text": "Food arrived cold and delayed by 40 minutes.",
        "star_rating": 1,
        "customer_name": "Siddharth Roy",
        "branch_name": "Bengaluru Indiranagar",
        "persona": "Empathetic & Solution-Oriented"
    }
    res = client.post("/api/v1/respond", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "response" in data
    assert "response_text" in data["response"]
    assert data["response"]["guardrail_passed"] is True
