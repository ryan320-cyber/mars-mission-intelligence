"""
FastAPI REST API Router for Mars Mission Intelligence.
Connects data ingestion, time-series analytics, statistical testing, anomaly detection,
challenge index, machine learning lab, and grounded AI assistant.
"""

from fastapi import APIRouter, Query, HTTPException, Body
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict, Any, List, Optional
import io
import csv
import json
import hashlib

from app.data.ingestion import ingestion_engine
from app.data.catalog import DATASET_CATALOG, get_catalog_summary
from app.analytics.time_series import (
    calculate_time_series_features, 
    downsample_time_series, 
    identify_sensor_gaps
)
from app.analytics.statistics import (
    compute_summary_statistics, 
    compute_correlation_matrix, 
    compare_missions
)
from app.analytics.anomaly import (
    detect_univariate_anomalies, 
    detect_multivariate_anomalies, 
    generate_event_replay
)
from app.analytics.challenge_index import calculate_meci, simulate_scenario
from app.ml.model_lab import run_model_experiment
from app.ai.grounded_scientist import query_mars_ai_scientist, PRESET_QUESTIONS

api_router = APIRouter()

# In-memory cached runs
_cached_ml_experiment: Optional[Dict[str, Any]] = None
_cached_multivariate_anomalies: Optional[List[Dict[str, Any]]] = None

@api_router.get("/overview")
def get_mission_overview() -> Dict[str, Any]:
    """High-level summary of Mars environmental intelligence status."""
    global _cached_multivariate_anomalies
    curiosity = ingestion_engine.ingest_curiosity_rems()
    insight = ingestion_engine.ingest_insight_meteorology()
    
    if _cached_multivariate_anomalies is None:
        _cached_multivariate_anomalies = detect_multivariate_anomalies(curiosity)

    latest_obs = curiosity[-1] if curiosity else {}
    
    # Calculate current MECI
    meci = calculate_meci(
        temp_amplitude_c=latest_obs.get("temp_amplitude_c"),
        pressure_pa=latest_obs.get("pressure_pa"),
        pressure_rate_of_change=0.8,
        solar_longitude_ls=latest_obs.get("solar_longitude_ls"),
        anomaly_intensity=15.0
    )

    return {
        "project_title": "Mars Mission Intelligence",
        "system_status": "OPERATIONAL",
        "data_freshness": "REAL NASA TELEMETRY CACHED",
        "total_observations": len(curiosity) + len(insight),
        "total_sols_recorded": len(curiosity),
        "active_datasets_count": len(DATASET_CATALOG),
        "anomalies_detected_count": len(_cached_multivariate_anomalies),
        "latest_curiosity_sol": latest_obs.get("sol"),
        "latest_terrestrial_date": latest_obs.get("terrestrial_date"),
        "latest_pressure_pa": latest_obs.get("pressure_pa"),
        "latest_temp_max_c": latest_obs.get("air_temp_max_c"),
        "latest_temp_min_c": latest_obs.get("air_temp_min_c"),
        "latest_temp_amplitude_c": latest_obs.get("temp_amplitude_c"),
        "latest_solar_longitude_ls": latest_obs.get("solar_longitude_ls"),
        "latest_season": latest_obs.get("martian_season"),
        "current_meci": meci
    }

@api_router.get("/catalog")
def get_catalog() -> Dict[str, Any]:
    """Inspect authoritative NASA Data Catalog with metadata and provenance."""
    return {
        "datasets": DATASET_CATALOG,
        "summary": get_catalog_summary()
    }

@api_router.get("/scorecard")
def get_data_quality_scorecard() -> Dict[str, Any]:
    """Data Quality layer with schema, physical range, duplicate, and gap checks."""
    return ingestion_engine.generate_quality_scorecard()

@api_router.get("/observations")
def get_observations(
    mission: str = Query("curiosity", description="Mission ID: curiosity or insight"),
    start_sol: Optional[int] = Query(None, description="Starting Sol filter"),
    end_sol: Optional[int] = Query(None, description="Ending Sol filter"),
    downsample: bool = Query(True, description="Downsample large records for rendering performance"),
    max_points: int = Query(400, description="Max downsampled points")
) -> Dict[str, Any]:
    """Query verified observational time series."""
    if mission.lower() in ["curiosity", "msl"]:
        records = ingestion_engine.ingest_curiosity_rems()
    elif mission.lower() in ["insight"]:
        records = ingestion_engine.ingest_insight_meteorology()
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported mission '{mission}'. Choose 'curiosity' or 'insight'.")

    # Apply Sol filters
    if start_sol is not None:
        records = [r for r in records if r.get("sol", 0) >= start_sol]
    if end_sol is not None:
        records = [r for r in records if r.get("sol", 0) <= end_sol]

    total_matched = len(records)
    
    # Identify sensor gaps
    sensor_gaps = identify_sensor_gaps(records, sol_gap_threshold=3)

    if downsample and total_matched > max_points:
        display_records = downsample_time_series(records, max_points=max_points)
    else:
        display_records = records

    return {
        "mission": mission,
        "total_matched": total_matched,
        "returned_points": len(display_records),
        "is_downsampled": bool(downsample and total_matched > max_points),
        "sensor_gaps": sensor_gaps,
        "observations": display_records
    }

@api_router.get("/profiles")
def get_vertical_profiles() -> Dict[str, Any]:
    """Retrieve MRO Mars Climate Sounder (MCS) vertical atmospheric sounding profiles."""
    profiles = ingestion_engine.ingest_mcs_profiles()
    return {
        "dataset_name": "MRO Mars Climate Sounder (MCS) Level 2 DDR",
        "vertical_layers": 25,
        "max_altitude_km": 80.0,
        "profiles": profiles
    }

@api_router.get("/anomalies")
def get_anomalies(
    variable: str = Query("air_temp_max_c", description="Variable for univariate detection"),
    threshold: float = Query(3.0, description="Modified Z-score threshold")
) -> Dict[str, Any]:
    """Univariate (Robust Z-Score) and Multivariate (Isolation Forest) anomalies."""
    global _cached_multivariate_anomalies
    curiosity = ingestion_engine.ingest_curiosity_rems()
    
    univariate = detect_univariate_anomalies(curiosity, variable=variable, threshold=threshold)
    
    if _cached_multivariate_anomalies is None:
        _cached_multivariate_anomalies = detect_multivariate_anomalies(curiosity)

    return {
        "variable_analyzed": variable,
        "univariate_count": len(univariate),
        "univariate_anomalies": univariate[:50],
        "multivariate_count": len(_cached_multivariate_anomalies),
        "multivariate_anomalies": _cached_multivariate_anomalies[:40],
        "methodology": "Robust Z-Score (Median Absolute Deviation) + Multivariate Isolation Forest"
    }

@api_router.get("/replay/{target_sol}")
def get_event_replay(target_sol: int) -> Dict[str, Any]:
    """Signature WOW Moment #1: Mars Environmental Event Replay (T-12 to T+12 Sols)."""
    curiosity = ingestion_engine.ingest_curiosity_rems()
    replay = generate_event_replay(curiosity, target_sol=target_sol)
    if not replay:
        raise HTTPException(status_code=404, detail=f"Sol {target_sol} not found in observation series.")
    return replay

@api_router.get("/statistics/summary")
def get_statistics_summary(variable: str = Query("air_temp_max_c")) -> Dict[str, Any]:
    """Compute summary statistics for a given variable."""
    curiosity = ingestion_engine.ingest_curiosity_rems()
    vals = [r.get(variable) for r in curiosity if r.get(variable) is not None]
    stats = compute_summary_statistics(vals)
    return {
        "variable": variable,
        "statistics": stats
    }

@api_router.get("/statistics/correlation")
def get_correlation_matrix() -> Dict[str, Any]:
    """Interactive Pearson and Spearman correlation matrices with p-values."""
    curiosity = ingestion_engine.ingest_curiosity_rems()
    variables = ["air_temp_max_c", "air_temp_min_c", "temp_amplitude_c", "pressure_pa", "solar_longitude_ls"]
    return compute_correlation_matrix(curiosity, variables)

@api_router.get("/statistics/comparison")
def get_mission_comparison() -> Dict[str, Any]:
    """Cross-mission hypothesis testing (Curiosity Gale Crater vs InSight Elysium Planitia)."""
    curiosity = ingestion_engine.ingest_curiosity_rems()
    insight = ingestion_engine.ingest_insight_meteorology()
    return compare_missions(curiosity, insight)

@api_router.get("/challenge-index")
def get_challenge_index() -> Dict[str, Any]:
    """Martian Environmental Challenge Index with factor decomposition."""
    curiosity = ingestion_engine.ingest_curiosity_rems()
    latest = curiosity[-1] if curiosity else {}
    return calculate_meci(
        temp_amplitude_c=latest.get("temp_amplitude_c"),
        pressure_pa=latest.get("pressure_pa"),
        pressure_rate_of_change=1.2,
        solar_longitude_ls=latest.get("solar_longitude_ls"),
        anomaly_intensity=25.0
    )

@api_router.post("/challenge-index/simulate")
def post_challenge_index_simulation(
    temp_variability_multiplier: float = Body(1.2, embed=True),
    hypothetical_pressure_drop_pa: float = Body(15.0, embed=True),
    dust_storm_active: bool = Body(False, embed=True)
) -> Dict[str, Any]:
    """Execute simulated What-If scenario analysis."""
    curiosity = ingestion_engine.ingest_curiosity_rems()
    latest = curiosity[-1] if curiosity else {}
    base_meci = calculate_meci(
        temp_amplitude_c=latest.get("temp_amplitude_c"),
        pressure_pa=latest.get("pressure_pa"),
        pressure_rate_of_change=1.0,
        solar_longitude_ls=latest.get("solar_longitude_ls"),
        anomaly_intensity=10.0
    )
    return simulate_scenario(
        base_meci=base_meci,
        temp_variability_multiplier=temp_variability_multiplier,
        pressure_drop_pa=hypothetical_pressure_drop_pa,
        inject_dust_storm=dust_storm_active
    )

@api_router.get("/model-lab")
def get_model_lab() -> Dict[str, Any]:
    """ML Model Lab: Baselines vs ML, chronological splits, feature importances, failure analysis."""
    global _cached_ml_experiment
    if _cached_ml_experiment is None:
        curiosity = ingestion_engine.ingest_curiosity_rems()
        _cached_ml_experiment = run_model_experiment(curiosity)
    return _cached_ml_experiment

@api_router.get("/ai/presets")
def get_ai_preset_questions() -> List[Dict[str, str]]:
    """Preset scientific inquiries."""
    return PRESET_QUESTIONS

@api_router.post("/ai/query")
def post_ai_query(
    query: str = Body(..., embed=True)
) -> Dict[str, Any]:
    """Grounded Mars AI Science Assistant with evidence tracing and anti-hallucination contract."""
    curiosity = ingestion_engine.ingest_curiosity_rems()
    anomalies = detect_multivariate_anomalies(curiosity)[:5]
    latest = curiosity[-1] if curiosity else {}
    meci = calculate_meci(
        temp_amplitude_c=latest.get("temp_amplitude_c"),
        pressure_pa=latest.get("pressure_pa"),
        pressure_rate_of_change=1.0,
        solar_longitude_ls=latest.get("solar_longitude_ls")
    )

    context = {
        "total_observations": len(curiosity),
        "latest_sol": latest.get("sol"),
        "anomalies": anomalies,
        "challenge_index": meci
    }
    return query_mars_ai_scientist(query, context)

@api_router.get("/export")
def export_dataset(
    mission: str = Query("curiosity"),
    format: str = Query("json", description="json or csv")
):
    """Export filtered observations with SHA-256 integrity hash."""
    records = ingestion_engine.ingest_curiosity_rems() if mission == "curiosity" else ingestion_engine.ingest_insight_meteorology()
    
    if format == "csv":
        output = io.StringIO()
        if records:
            writer = csv.DictWriter(output, fieldnames=list(records[0].keys()))
            writer.writeheader()
            writer.writerows(records)
        content = output.getvalue()
        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        
        response = StreamingResponse(
            io.StringIO(content),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={mission}_mars_telemetry.csv",
                "X-Dataset-SHA256": sha256
            }
        )
        return response
    else:
        content_str = json.dumps(records, indent=2)
        sha256 = hashlib.sha256(content_str.encode("utf-8")).hexdigest()
        return JSONResponse(
            content={"metadata": {"mission": mission, "count": len(records), "sha256": sha256}, "data": records}
        )
