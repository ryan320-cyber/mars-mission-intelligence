"""
Tests for Data Integrity, Provenance Tracking, Date Validation, and Quality Scorecard.
Fulfills Rule 1, Rule 2, Part 3.2, Part 4.1, Part 4.3.
"""

import pytest
from app.data.ingestion import ingestion_engine
from app.core.data_loader import data_loader

def test_invalid_dates_detected_and_rejected():
    """Verify that impossible dates (like month 13, day 32) are detected and rejected."""
    # Test impossible month
    is_valid, reason = ingestion_engine.validate_date("2019-13-18")
    assert not is_valid
    assert "13" in reason or "Impossible month" in reason

    # Test impossible day
    is_valid_day, reason_day = ingestion_engine.validate_date("2020-02-31")
    assert not is_valid_day
    assert "Invalid calendar date" in reason_day or "day" in reason_day

    # Test malformed pattern
    is_valid_malformed, _ = ingestion_engine.validate_date("2020/05/12")
    assert not is_valid_malformed

    # Test authentic valid dates
    is_valid_curio, _ = ingestion_engine.validate_date("2012-08-07")
    assert is_valid_curio

def test_insight_utc_astronomical_derivation():
    """Verify authentic UTC derivation for InSight Sols from landing epoch (2018-11-26)."""
    # Sol 0 must be InSight landing date
    assert ingestion_engine.derive_utc_from_insight_sol(0) == "2018-11-26"

    # Sol 10
    sol_10_date = ingestion_engine.derive_utc_from_insight_sol(10)
    assert sol_10_date == "2018-12-06"
    is_valid, _ = ingestion_engine.validate_date(sol_10_date)
    assert is_valid

    # Sol 720 (previously month 13 bug)
    sol_720_date = ingestion_engine.derive_utc_from_insight_sol(720)
    assert sol_720_date == "2020-12-04"
    is_valid_720, _ = ingestion_engine.validate_date(sol_720_date)
    assert is_valid_720

def test_synthetic_data_provenance_labeling():
    """Verify synthetic / simulated baseline records are explicitly tagged DEMONSTRATION DATA."""
    insight_records = data_loader.get_insight_records()
    assert len(insight_records) > 0

    for rec in insight_records:
        if rec.get("is_synthetic"):
            assert rec.get("data_provenance") == "DEMONSTRATION DATA"
            assert rec.get("data_origin") == "simulated"
            assert rec.get("provenance_status") == "SYNTHETIC_DEMONSTRATION"

def test_curiosity_observed_data_labeling():
    """Verify authentic Curiosity records are tagged observed / VERIFIED_AUTHORITATIVE."""
    curiosity_records = data_loader.get_curiosity_records()
    assert len(curiosity_records) >= 4000

    sample = curiosity_records[100]
    assert sample.get("data_origin") == "observed"
    assert sample.get("is_synthetic") is False
    assert sample.get("provenance_status") == "VERIFIED_AUTHORITATIVE"
    assert sample.get("dataset_id") == "MSL-M-REMS-MOD-5-V1.0"

def test_mcs_profiles_uncertainty_and_provenance():
    """Verify MRO MCS vertical profiles include 1-sigma uncertainty and demonstration tagging."""
    mcs_profiles = data_loader.get_mcs_profiles()
    assert len(mcs_profiles) == 4

    for prof in mcs_profiles:
        assert prof.get("data_provenance") == "DEMONSTRATION DATA"
        assert prof.get("is_synthetic") is True
        assert len(prof["levels"]) == 25
        for lvl in prof["levels"]:
            assert "temperature_uncertainty_k" in lvl
            assert lvl["temperature_uncertainty_k"] > 0

def test_dynamic_quality_scorecard_metrics():
    """Verify quality scorecard calculates empirical metrics without hardcoding."""
    scorecard = ingestion_engine.generate_quality_scorecard()

    assert "curiosity_msl" in scorecard
    curio = scorecard["curiosity_msl"]
    assert curio["total_source_records"] >= 4000
    assert curio["invalid_dates_count"] == 0
    assert curio["duplicate_sols_count"] == 0
    assert curio["completeness_pressure_pct"] > 80.0
    assert curio["completeness_temperature_pct"] > 80.0
    assert curio["data_origin"] == "observed"

    assert "insight_apss" in scorecard
    insight = scorecard["insight_apss"]
    assert insight["invalid_dates_count"] == 0
    assert insight["is_synthetic"] is True
    assert insight["data_provenance"] == "DEMONSTRATION DATA"

    assert "mro_mcs" in scorecard
    mcs = scorecard["mro_mcs"]
    assert mcs["profiles_count"] == 4
    assert mcs["uncertainty_coverage_pct"] == 100.0
