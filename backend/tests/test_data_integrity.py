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
    """Verify authentic Curiosity records are tagged observed and CACHED_VERIFIED_SOURCE."""
    curiosity_records = data_loader.get_curiosity_records()
    assert len(curiosity_records) >= 4000

    sample = curiosity_records[100]
    assert sample.get("data_origin") == "observed"
    assert sample.get("is_synthetic") is False
    assert sample.get("provenance_status") in ["CACHED_VERIFIED_SOURCE", "VERIFIED_AUTHORITATIVE"]
    assert sample.get("dataset_id") == "NASA-MSL-WEATHER-RSS"
    assert sample.get("source_authenticity") == "VERIFIED_NASA_MARS_WEATHER_API"
    assert sample.get("structural_validity") == "VALID"

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

def test_date_validity_does_not_confer_source_verification():
    """Phase 3 Regression: Date validity establishes calendar validity only, NOT source authenticity."""
    from app.data.ingestion import ProvenanceStatus
    # Record with a completely valid calendar date but unverified/unknown source
    unverified_records = [{
        "sol": 9999,
        "terrestrial_date": "2024-06-15",
        "data_source": "Unknown Scraping Script",
        "dataset_id": "UNKNOWN_ID"
    }]
    # Validate with is_source_verified=False
    tagged = ingestion_engine._validate_and_tag_curiosity(unverified_records, is_source_verified=False)
    assert len(tagged) == 1
    # Must NOT receive CACHED_VERIFIED_SOURCE or VERIFIED_AUTHORITATIVE
    assert tagged[0]["provenance_status"] == ProvenanceStatus.UNVERIFIED_SOURCE
    assert tagged[0]["source_authenticity"] == "UNVERIFIED"
    assert tagged[0]["structural_validity"] == "VALID"

def test_distinct_provenance_states():
    """Phase 3 Regression: Verify all distinct provenance states are defined and non-overlapping."""
    from app.data.ingestion import ProvenanceStatus
    states = [
        ProvenanceStatus.VERIFIED_SOURCE,
        ProvenanceStatus.CACHED_VERIFIED_SOURCE,
        ProvenanceStatus.UNVERIFIED_SOURCE,
        ProvenanceStatus.SYNTHETIC,
        ProvenanceStatus.DERIVED,
        ProvenanceStatus.UNAVAILABLE
    ]
    # All 6 primary states must have distinct values
    assert len(set(states)) == 6

def test_processed_curiosity_records_provenance_status():
    """Phase 3 Regression: Verify _process_curiosity_records and scorecard use CACHED_VERIFIED_SOURCE."""
    from app.data.ingestion import ingestion_engine, ProvenanceStatus
    raw_mock = [{
        "sol": "5000",
        "terrestrial_date": "2026-09-01",
        "ls": "180.0",
        "min_temp": "-75.0",
        "max_temp": "-10.0",
        "pressure": "850.0"
    }]
    processed = ingestion_engine._process_curiosity_records(raw_mock)
    assert len(processed) == 1
    assert processed[0]["provenance_status"] == ProvenanceStatus.CACHED_VERIFIED_SOURCE.value

    scorecard = ingestion_engine.generate_quality_scorecard()
    curio_card = scorecard.get("curiosity_msl", {})
    assert curio_card.get("provenance_status") == ProvenanceStatus.CACHED_VERIFIED_SOURCE.value

def test_self_declared_mission_name_cannot_confer_source_verification():
    """Phase 2.1 Regression: Merely naming NASA/REMS/MSL in a record cannot verify it."""
    from app.data.ingestion import ingestion_engine, ProvenanceStatus
    fabricated_records = [
        {
            "sol": 3000,
            "terrestrial_date": "2021-01-01",
            "data_source": "NASA REMS MSL CURIOSITY OFFICIAL TELEMETRY",
            "dataset_id": "NASA-MSL-WEATHER-RSS",
            "mission": "MSL Curiosity"
        }
    ]
    # Ingestion evaluation with unverified channel
    tagged = ingestion_engine._validate_and_tag_curiosity(fabricated_records, is_source_verified=False)
    assert len(tagged) == 1
    assert tagged[0]["provenance_status"] == ProvenanceStatus.UNVERIFIED_SOURCE
    assert tagged[0]["source_authenticity"] == "UNVERIFIED"

def test_missing_weather_readings_remain_none_not_invented_strings():
    """Phase 6.2 Regression: Missing sensor fields must be None, never invented placeholders like 'Sunny'."""
    from app.data.ingestion import ingestion_engine
    raw_record_missing_fields = [{
        "sol": "5001",
        "terrestrial_date": "2026-09-02",
        "ls": "181.0",
        "min_temp": "-70.0",
        "max_temp": "-15.0",
        "pressure": "840.0"
        # intentionally omitting wind_speed, atmo_opacity, season
    }]
    processed = ingestion_engine._process_curiosity_records(raw_record_missing_fields)
    assert len(processed) == 1
    rec = processed[0]
    assert rec["wind_speed_ms"] is None
    assert rec["atmospheric_opacity"] is None
    assert rec["pressure_string"] is None

def test_data_loader_defensive_copies_prevent_cache_mutation():
    """Phase 6.3 Regression: Mutating returned records must not mutate the internal cache."""
    recs = data_loader.get_curiosity_records()
    orig_sol = recs[0]["sol"]
    orig_count = len(recs)

    # Attempt mutation
    recs[0]["sol"] = 999999
    recs.pop()

    # Re-fetch from data_loader
    recs_after = data_loader.get_curiosity_records()
    assert recs_after[0]["sol"] == orig_sol
    assert len(recs_after) == orig_count

    # Test get_sol_record mutation protection
    sol_rec = data_loader.get_sol_record(orig_sol)
    assert sol_rec is not None
    sol_rec["pressure_pa"] = -99999.9
    sol_rec_fresh = data_loader.get_sol_record(orig_sol)
    assert sol_rec_fresh["pressure_pa"] != -99999.9


