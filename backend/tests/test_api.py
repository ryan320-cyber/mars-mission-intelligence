import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"

def test_get_mission_overview():
    res = client.get("/api/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["project_title"] == "Mars Mission Intelligence"
    assert data["total_observations"] > 4000
    assert "current_meci" in data

def test_get_catalog():
    res = client.get("/api/catalog")
    assert res.status_code == 200
    data = res.json()
    assert "msl_curiosity_rems" in data["datasets"]
    assert "insight_twins_apss" in data["datasets"]
    assert "mro_mcs_profiles" in data["datasets"]

def test_get_scorecard():
    res = client.get("/api/scorecard")
    assert res.status_code == 200
    data = res.json()
    assert "curiosity_msl" in data
    assert data["curiosity_msl"]["schema_check"].startswith("PASS")

def test_get_observations():
    res = client.get("/api/observations?mission=curiosity&max_points=50")
    assert res.status_code == 200
    data = res.json()
    assert data["mission"] == "curiosity"
    assert data["returned_points"] <= 55
    assert len(data["observations"]) > 0

def test_get_profiles():
    res = client.get("/api/profiles")
    assert res.status_code == 200
    data = res.json()
    assert len(data["profiles"]) > 0
    assert len(data["profiles"][0]["levels"]) == 25

def test_get_anomalies():
    res = client.get("/api/anomalies")
    assert res.status_code == 200
    data = res.json()
    assert data["multivariate_count"] > 0

def test_get_challenge_index():
    res = client.get("/api/challenge-index")
    assert res.status_code == 200
    data = res.json()
    assert 0 <= data["index_score"] <= 100

def test_post_ai_query():
    res = client.post("/api/ai/query", json={"query": "Explain the major detected anomalies"})
    assert res.status_code == 200
    data = res.json()
    assert "finding" in data
    assert "data_evidence" in data
    assert "analytical_interpretation" in data
    assert "limitations" in data
    assert "source" in data
