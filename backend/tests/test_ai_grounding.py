"""
Tests for Grounded AI Scientist: Epistemic Guardrails, Anti-Hallucination,
and Structured AI Answer Contract.
Fulfills Rule 3, Part 8.1 - 8.4.
"""

import pytest
from app.ai.grounded_scientist import query_mars_ai_scientist, PRESET_QUESTIONS

MOCK_CONTEXT = {
    "total_observations": 4745,
    "latest_sol": 4995,
    "anomalies": [
        {
            "sol": 2082,
            "severity": "EXTREME",
            "anomaly_intensity": 91.2,
            "primary_contributors": ["Drastic Diurnal Temperature Collapse"]
        }
    ],
    "challenge_index": {
        "index_score": 58.4,
        "classification": "HIGH"
    }
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
