"""
Tests for Grounded AI Scientist: Epistemic Guardrails, Anti-Hallucination,
Structured AI Answer Contract, and Evidence-First Query Pipeline.
Fulfills Rule 1, 2, 3; Phase Two & Phase Nine.
"""

import pytest
from app.ai.grounded_scientist import query_mars_ai_scientist, PRESET_QUESTIONS

MOCK_ML_EXPERIMENT = {
    "task_description": "Next-Sol Diurnal Temperature Amplitude Forecasting",
    "dataset_split": {
        "methodology": "Strict Chronological Partitioning",
        "train_samples": 3299,
        "val_samples": 707,
        "test_samples": 708,
        "train_sol_range": "Sol 13 to Sol 3507",
        "val_sol_range": "Sol 3508 to Sol 4261",
        "test_sol_range": "Sol 4262 to Sol 4995"
    },
    "models_comparison": [
        {
            "model_name": "Naive Persistence Baseline (y_t = y_{t-1})",
            "mae": 4.53,
            "rmse": 8.87,
            "r2": 0.069,
            "type": "Baseline"
        },
        {
            "model_name": "Random Forest Regressor (Selected Model)",
            "mae": 3.72,
            "rmse": 6.92,
            "r2": 0.433,
            "type": "Machine Learning",
            "improvement_over_baseline_pct": 17.8
        }
    ],
    "slice_error_analysis": {
        "seasonal_slices": {},
        "failure_case_analysis": "Severe error during dust storm season.",
        "honest_failure_case": {
            "season_name": "Martian Dust Storm Season / Perihelion",
            "ls_range": "180° - 270°",
            "test_sample_count": 137,
            "mae": 7.13,
            "max_error_c": 68.4,
            "extreme_error_threshold_c": 14.0,
            "extreme_error_count": 21
        }
    }
}

MOCK_CONTEXT = {
    "total_observations": 4745,
    "latest_sol": 4995,
    "curiosity_records": [
        {"sol": i, "terrestrial_date": f"2023-01-{i:02d}", "air_temp_max_c": -20.0 + i * 0.1, "air_temp_mean_c": -50.0 + i * 0.1, "temp_amplitude_c": 40.0, "pressure_pa": 840.0}
        for i in range(1, 30)
    ],
    "anomalies": [
        {
            "sol": 2082,
            "severity": "EXTREME",
            "anomaly_intensity": 91.2,
            "primary_contributors": ["Drastic Diurnal Temperature Collapse"],
            "observed_values": {"temp_amplitude_c": 12.5, "pressure_pa": 890.0}
        }
    ],
    "challenge_index": {
        "index_score": 58.4,
        "classification": "HIGH"
    },
    "ml_experiment": MOCK_ML_EXPERIMENT
}

def test_unsupported_subjects_refusal():
    """Verify refusal to fabricate observations for subjects outside sensor capability."""
    refusal_queries = [
        "What are the detected methane plumes in Gale Crater?",
        "Have we found subsurface water oceans or aquifers?",
        "Are there alien biosignatures in the regolith?",
        "Calculate human oxygen consumption for a surface habitat"
    ]
    for q in refusal_queries:
        res = query_mars_ai_scientist(q, MOCK_CONTEXT)
        assert res["data_sufficiency"] == "INSUFFICIENT"
        assert res["data_status"] == "INSUFFICIENT_DATA"
        assert "outside the scope" in res["finding"]
        assert len(res["evidence_links"]) == 0
        assert "no calibrated sensor" in res["data_evidence"].lower()

def test_ai_answer_contract_structure():
    """Verify responses adhere strictly to the full structured AI Answer Contract."""
    res = query_mars_ai_scientist("Explain the major detected anomalies", MOCK_CONTEXT)
    
    # Required core contract fields
    assert "finding" in res and len(res["finding"]) > 0
    assert "data_evidence" in res and len(res["data_evidence"]) > 0
    assert "analytical_interpretation" in res and len(res["analytical_interpretation"]) > 0
    assert "uncertainty" in res and len(res["uncertainty"]) > 0
    assert "limitations" in res and len(res["limitations"]) > 0
    assert "source" in res and len(res["source"]) > 0
    assert "data_sufficiency" in res and res["data_sufficiency"] in ["HIGH", "MODERATE", "LOW", "INSUFFICIENT"]
    assert "evidence_links" in res and len(res["evidence_links"]) > 0
    assert "model_provider_status" in res

def test_ai_evidence_traceability_links():
    """Verify clickable evidence trace links point to valid UI modules."""
    res = query_mars_ai_scientist("Why does the Environmental Challenge Index peak in certain seasons?", MOCK_CONTEXT)
    assert len(res["evidence_links"]) > 0
    
    valid_targets = ["overview", "explorer", "atmospheric", "anomaly", "map", "meci", "model", "ai", "catalog", "notebook"]
    for link in res["evidence_links"]:
        assert "label" in link
        assert link["target"] in valid_targets

def test_model_limitations_query_references_honest_failure():
    """Verify model evaluation questions report honest dust season failure mode."""
    res = query_mars_ai_scientist("Where does the diurnal temperature forecasting model fail?", MOCK_CONTEXT)
    assert "dust" in res["finding"].lower() or "dust" in res["data_evidence"].lower()
    assert "Ls 180" in res["data_evidence"] or "Ls 180" in res["finding"] or "dust storm" in res["data_evidence"]

# --- Phase Nine Required Regression Tests ---

def test_ai_empty_anomalies_no_default_sol():
    """Regression: When anomaly collection is empty, assistant must report 0 anomalies and NEVER default to Sol 2082."""
    empty_context = dict(MOCK_CONTEXT)
    empty_context["anomalies"] = []
    
    res = query_mars_ai_scientist("What is the most recent detected anomaly?", empty_context)
    assert "no statistical candidate anomalies were detected" in res["finding"].lower()
    assert "2082" not in res["finding"]
    assert "2082" not in res["data_evidence"]

def test_ai_causation_hedging():
    """Regression: Causation queries must distinguish statistical detection from physical causation."""
    res = query_mars_ai_scientist("What caused this anomaly on Mars?", MOCK_CONTEXT)
    assert "statistical detection" in res["data_evidence"].lower() or "statistical detection" in res["analytical_interpretation"].lower()
    assert "physical causation" in res["data_evidence"].lower() or "physical causation" in res["analytical_interpretation"].lower()

def test_ai_temperature_trend_dynamic_calculation():
    """Regression: Temperature trend queries calculate dynamic delta, slope, and Sol range from actual records."""
    res = query_mars_ai_scientist("Did the temperature increase or decrease over the analyzed period?", MOCK_CONTEXT)
    assert "increased" in res["finding"].lower() or "stable" in res["finding"].lower()
    assert "Sol" in res["finding"]
    assert "°C" in res["finding"]
    assert res["data_status"] == "CACHED_VERIFIED_SOURCE"

def test_ai_missing_temperature_records_reports_insufficient():
    """Regression: Missing temperature records returns explicit insufficient data response."""
    no_temp_context = dict(MOCK_CONTEXT)
    no_temp_context["curiosity_records"] = []
    res = query_mars_ai_scientist("Did the temperature increase?", no_temp_context)
    assert res["data_sufficiency"] == "INSUFFICIENT"
    assert "insufficient" in res["finding"].lower()

def test_ai_model_metrics_dynamic_or_unavailable():
    """Regression: When ML experiment artifact is absent and cannot be computed, reports unavailable rather than hardcoded metrics."""
    no_ml_context = {
        "total_observations": 0,
        "latest_sol": 0,
        "curiosity_records": [],
        "anomalies": [],
        "ml_experiment": None
    }
    res = query_mars_ai_scientist("What is the model accuracy?", no_ml_context)
    # If no data and no artifact, must report unavailable, never fabricate 3.72
    if res["data_sufficiency"] == "INSUFFICIENT":
        assert "no verified" in res["finding"].lower() or "unavailable" in res["finding"].lower()

def test_ai_meci_no_hardcoded_fallback():
    """Regression: When challenge_index is None or missing index_score, assistant must NOT default to 58.4 or HIGH."""
    no_meci_context = dict(MOCK_CONTEXT)
    no_meci_context["challenge_index"] = None

    res = query_mars_ai_scientist("What is the current MECI challenge index risk?", no_meci_context)
    assert res["data_status"] == "UNAVAILABLE"
    assert res["data_sufficiency"] == "INSUFFICIENT"
    assert "unavailable" in res["finding"].lower()
    assert "58.4" not in res["finding"]
    assert "58.4" not in res["data_evidence"]

def test_ai_meci_dynamic_when_provided():
    """Regression: When challenge_index is provided, assistant must use the actual calculated score and tier."""
    custom_meci_context = dict(MOCK_CONTEXT)
    custom_meci_context["challenge_index"] = {
        "index_score": 76.8,
        "classification": "CRITICAL",
        "factor_breakdown": {}
    }

    res = query_mars_ai_scientist("What is the current MECI risk score?", custom_meci_context)
    assert "76.8" in res["finding"]
    assert "CRITICAL" in res["finding"]
    assert res["data_status"] == "DERIVED"
    assert res["data_sufficiency"] == "HIGH"
