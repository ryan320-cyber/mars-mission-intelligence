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

    # Test trailing slash returns 200 directly without 308 redirect
    res_slash = client.get("/api/overview/", follow_redirects=False)
    assert res_slash.status_code == 200

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

def test_cors_headers():
    origin = "https://mars-mission-intelligence-pzjo.vercel.app"
    res = client.options(
        "/api/overview",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == origin

    # Test local dev origin
    local_origin = "http://localhost:5173"
    res_local = client.options(
        "/api/overview",
        headers={
            "Origin": local_origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res_local.status_code == 200
    assert res_local.headers.get("access-control-allow-origin") == local_origin

def test_profile_downsampling():
    # Full profiles
    res_full = client.get("/api/profiles?downsample=false")
    assert res_full.status_code == 200
    full_data = res_full.json()
    assert len(full_data["profiles"][0]["levels"]) == 25

    # Downsampled profiles (retaining 15 levels with 1-sigma uncertainty preserved)
    res_down = client.get("/api/profiles?downsample=true&target_levels=15")
    assert res_down.status_code == 200
    down_data = res_down.json()
    assert len(down_data["profiles"][0]["levels"]) <= 16
    assert down_data["profiles"][0]["levels"][0]["altitude_km"] == 0.0

def test_sol_replay_fast_response():
    # Warm up client / route
    _ = client.get("/api/replay/2082")

    import time
    start = time.perf_counter()
    res = client.get("/api/replay/2082")
    duration_ms = (time.perf_counter() - start) * 1000
    assert res.status_code == 200
    data = res.json()
    assert data["target_sol"] == 2082
    assert len(data["replay_timeline"]) > 0

    # Also test the underlying algorithmic reconstruction latency
    from app.core.data_loader import data_loader
    from app.analytics.anomaly import generate_event_replay
    recs = data_loader.get_curiosity_records()
    t_start = time.perf_counter()
    replay = generate_event_replay(recs, 2082)
    algo_ms = (time.perf_counter() - t_start) * 1000
    assert replay is not None
    assert algo_ms < 20.0  # Core algorithmic replay reconstruction runs in < 20ms

def test_unsupported_variable_returns_400():
    """Phase 5.1 Regression: Unsupported or non-numeric variables return HTTP 400."""
    res_cat = client.get("/api/statistics/summary?variable=martian_season")
    assert res_cat.status_code == 400
    assert "Unsupported numerical variable" in res_cat.json()["detail"]

    res_missing = client.get("/api/statistics/summary?variable=non_existent_var")
    assert res_missing.status_code == 400
    assert "Unsupported numerical variable" in res_missing.json()["detail"]

    res_anomaly_cat = client.get("/api/anomalies?variable=martian_season")
    assert res_anomaly_cat.status_code == 400
    assert "Unsupported numerical variable" in res_anomaly_cat.json()["detail"]

def test_invalid_anomaly_threshold_returns_400():
    """Phase 5.4 Regression: Non-positive or out-of-range anomaly thresholds return HTTP 400."""
    res_zero = client.get("/api/anomalies?threshold=0")
    assert res_zero.status_code == 400
    assert "strictly positive" in res_zero.json()["detail"]

    res_neg = client.get("/api/anomalies?threshold=-1.5")
    assert res_neg.status_code == 400
    assert "strictly positive" in res_neg.json()["detail"]

    res_huge = client.get("/api/anomalies?threshold=100.0")
    assert res_huge.status_code == 400

def test_downsample_bounds_validation():
    """Phase 5.2 & 5.3 Regression: Invalid downsampling and level limits return HTTP 422."""
    res_pts_zero = client.get("/api/observations?mission=curiosity&max_points=0")
    assert res_pts_zero.status_code == 422

    res_pts_one = client.get("/api/observations?mission=curiosity&max_points=1")
    assert res_pts_one.status_code == 422

    res_pts_huge = client.get("/api/observations?mission=curiosity&max_points=5001")
    assert res_pts_huge.status_code == 422

    res_lvl_zero = client.get("/api/profiles?downsample=true&target_levels=0")
    assert res_lvl_zero.status_code == 422

    res_lvl_two = client.get("/api/profiles?downsample=true&target_levels=2")
    assert res_lvl_two.status_code == 422

    res_lvl_huge = client.get("/api/profiles?downsample=true&target_levels=101")
    assert res_lvl_huge.status_code == 422

def test_meci_score_identical_across_overview_and_challenge_index():
    """Phase 3.1 Regression: MECI score must be identical across overview and dedicated endpoint."""
    res_overview = client.get("/api/overview")
    assert res_overview.status_code == 200
    overview_meci = res_overview.json()["current_meci"]["index_score"]

    res_ci = client.get("/api/challenge-index")
    assert res_ci.status_code == 200
    ci_meci = res_ci.json()["index_score"]

    assert overview_meci == ci_meci

def test_export_validation_rejects_unsupported_mission_and_format():
    """Phase 6.1 Regression: Export endpoint rejects unsupported missions and formats with HTTP 400."""
    res_perseverance = client.get("/api/export?mission=perseverance&format=json")
    assert res_perseverance.status_code == 400
    assert "Unsupported export mission" in res_perseverance.json()["detail"]

    res_xml = client.get("/api/export?mission=curiosity&format=xml")
    assert res_xml.status_code == 400
    assert "Unsupported export format" in res_xml.json()["detail"]

    # Valid combinations return 200 with proper media types
    res_json = client.get("/api/export?mission=curiosity&format=json")
    assert res_json.status_code == 200
    assert "application/json" in res_json.headers.get("content-type", "")

    res_csv = client.get("/api/export?mission=curiosity&format=csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers.get("content-type", "")

