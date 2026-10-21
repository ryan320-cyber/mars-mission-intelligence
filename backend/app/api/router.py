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

from app.core.data_loader import data_loader
from app.data.ingestion import ingestion_engine
from app.data.catalog import DATASET_CATALOG, get_catalog_summary
from app.analytics.time_series import (
    calculate_time_series_features, 
    downsample_time_series, 
    downsample_vertical_profiles,
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
from app.analytics.challenge_index import calculate_meci, simulate_scenario, compute_current_meci_from_telemetry
from app.ml.model_lab import run_model_experiment
from app.ai.grounded_scientist import query_mars_ai_scientist, PRESET_QUESTIONS
import numpy as np

SUPPORTED_NUMERIC_VARIABLES = {
    "air_temp_max_c",
    "air_temp_min_c",
    "air_temp_mean_c",
    "temp_amplitude_c",
    "pressure_pa",
    "solar_longitude_ls"
}

api_router = APIRouter(redirect_slashes=False)

# In-memory cached runs
_cached_ml_experiment: Optional[Dict[str, Any]] = None
_cached_multivariate_anomalies: Optional[List[Dict[str, Any]]] = None

@api_router.get("/overview")
@api_router.get("/overview/", include_in_schema=False)
def get_mission_overview() -> Dict[str, Any]:
    """High-level summary of Mars environmental intelligence status."""
    global _cached_multivariate_anomalies
    curiosity = data_loader.get_curiosity_records()
    insight = data_loader.get_insight_records()
    
    if _cached_multivariate_anomalies is None:
        _cached_multivariate_anomalies = detect_multivariate_anomalies(curiosity)

    latest_obs = curiosity[-1] if curiosity else {}
    
    # Calculate unified current MECI
    meci = compute_current_meci_from_telemetry(curiosity, _cached_multivariate_anomalies)

    return {
        "project_title": "Mars Mission Intelligence",
        "system_status": "OPERATIONAL",
        "data_freshness": "NASA MARS WEATHER SERVICE FEED (CACHED)",
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
    max_points: int = Query(400, ge=2, le=5000, description="Max downsampled points (2 to 5000)")
) -> Dict[str, Any]:
    """Query verified observational time series."""
    if mission.lower() in ["curiosity", "msl"]:
        records = data_loader.get_curiosity_records()
    elif mission.lower() in ["insight"]:
        records = data_loader.get_insight_records()
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
def get_vertical_profiles(
    downsample: bool = Query(False, description="Downsample vertical sounding layers for smaller network payload"),
    target_levels: int = Query(15, ge=3, le=100, description="Number of target vertical levels to retain (3 to 100)")
) -> Dict[str, Any]:
    """Retrieve MRO Mars Climate Sounder (MCS) vertical atmospheric sounding profiles."""
    profiles = data_loader.get_mcs_profiles()
    if downsample:
        profiles = downsample_vertical_profiles(profiles, target_levels=target_levels)
    return {
        "dataset_name": "MRO Mars Climate Sounder (MCS) Level 2 DDR",
        "vertical_layers": len(profiles[0]["levels"]) if profiles else 25,
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
    curiosity = data_loader.get_curiosity_records()
    
    if variable not in SUPPORTED_NUMERIC_VARIABLES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported numerical variable '{variable}'. Supported variables are: {sorted(SUPPORTED_NUMERIC_VARIABLES)}"
        )
    if threshold <= 0 or not np.isfinite(threshold) or threshold > 50.0:
        raise HTTPException(
            status_code=400,
            detail=f"Anomaly threshold must be a strictly positive finite number in range (0.0, 50.0], got {threshold}."
        )

    univariate = detect_univariate_anomalies(curiosity, variable=variable, threshold=threshold)
    
    if _cached_multivariate_anomalies is None:
        _cached_multivariate_anomalies = detect_multivariate_anomalies(curiosity)

    return {
        "variable_analyzed": variable,
        "univariate_count": len(univariate),
        "univariate_anomalies": univariate[:50],
        "multivariate_count": len(_cached_multivariate_anomalies),
        "multivariate_anomalies": _cached_multivariate_anomalies[:40],
        "methodology": "Robust Z-Score (Vectorized Median Absolute Deviation) + Multivariate Isolation Forest"
    }

@api_router.get("/replay/{target_sol}")
def get_event_replay(target_sol: int) -> Dict[str, Any]:
    """Signature WOW Moment #1: Mars Environmental Event Replay (T-12 to T+12 Sols)."""
    curiosity = data_loader.get_curiosity_records()
    replay = generate_event_replay(curiosity, target_sol=target_sol)
    if not replay:
        raise HTTPException(status_code=404, detail=f"Sol {target_sol} not found in observation series.")
    return replay

@api_router.get("/statistics/summary")
def get_statistics_summary(variable: str = Query("air_temp_max_c")) -> Dict[str, Any]:
    """Compute summary statistics for a given variable."""
    if variable not in SUPPORTED_NUMERIC_VARIABLES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported numerical variable '{variable}'. Supported variables are: {sorted(SUPPORTED_NUMERIC_VARIABLES)}"
        )
    curiosity = data_loader.get_curiosity_records()
    vals = [r.get(variable) for r in curiosity if r.get(variable) is not None]
    stats = compute_summary_statistics(vals)
    return {
        "variable": variable,
        "statistics": stats
    }

@api_router.get("/statistics/correlation")
def get_correlation_matrix() -> Dict[str, Any]:
    """Interactive Pearson and Spearman correlation matrices with p-values."""
    curiosity = data_loader.get_curiosity_records()
    variables = ["air_temp_max_c", "air_temp_min_c", "temp_amplitude_c", "pressure_pa", "solar_longitude_ls"]
    return compute_correlation_matrix(curiosity, variables)

@api_router.get("/statistics/comparison")
def get_mission_comparison() -> Dict[str, Any]:
    """Cross-mission hypothesis testing (Curiosity Gale Crater vs InSight Elysium Planitia)."""
    curiosity = data_loader.get_curiosity_records()
    insight = data_loader.get_insight_records()
    return compare_missions(curiosity, insight)

@api_router.get("/challenge-index")
def get_challenge_index() -> Dict[str, Any]:
    """Martian Environmental Challenge Index with factor decomposition."""
    global _cached_multivariate_anomalies
    curiosity = data_loader.get_curiosity_records()
    if _cached_multivariate_anomalies is None:
        _cached_multivariate_anomalies = detect_multivariate_anomalies(curiosity)
    return compute_current_meci_from_telemetry(curiosity, _cached_multivariate_anomalies)

@api_router.post("/challenge-index/simulate")
def post_challenge_index_simulation(
    temp_variability_multiplier: float = Body(1.2, embed=True, ge=0.0, le=5.0),
    hypothetical_pressure_drop_pa: float = Body(15.0, embed=True, ge=0.0, le=500.0),
    dust_storm_active: bool = Body(False, embed=True)
) -> Dict[str, Any]:
    """Execute simulated What-If scenario analysis."""
    global _cached_multivariate_anomalies
    curiosity = data_loader.get_curiosity_records()
    if _cached_multivariate_anomalies is None:
        _cached_multivariate_anomalies = detect_multivariate_anomalies(curiosity)
    base_meci = compute_current_meci_from_telemetry(curiosity, _cached_multivariate_anomalies)
    return simulate_scenario(
        base_meci,
        temp_variability_multiplier=temp_variability_multiplier,
        pressure_drop_pa=hypothetical_pressure_drop_pa,
    )

@api_router.get("/model-lab")
def get_model_lab() -> Dict[str, Any]:
    """ML Model Lab: Baselines vs ML, chronological splits, feature importances, failure analysis."""
    global _cached_ml_experiment
    if _cached_ml_experiment is None:
        curiosity = data_loader.get_curiosity_records()
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
    global _cached_ml_experiment, _cached_multivariate_anomalies
    curiosity = data_loader.get_curiosity_records()
    insight = data_loader.get_insight_records()
    
    if _cached_multivariate_anomalies is None:
        _cached_multivariate_anomalies = detect_multivariate_anomalies(curiosity)
    
    if _cached_ml_experiment is None and len(curiosity) > 100:
        _cached_ml_experiment = run_model_experiment(curiosity)

    meci = compute_current_meci_from_telemetry(curiosity, _cached_multivariate_anomalies)
    latest = curiosity[-1] if curiosity else {}

    context = {
        "total_observations": len(curiosity),
        "latest_sol": latest.get("sol"),
        "curiosity_records": curiosity,
        "insight_records": insight,
        "anomalies": _cached_multivariate_anomalies or [],
        "challenge_index": meci,
        "ml_experiment": _cached_ml_experiment
    }
    return query_mars_ai_scientist(query, context)

@api_router.get("/export")
def export_dataset(
    mission: str = Query("curiosity"),
    format: str = Query("json", description="json or csv")
):
    """Export filtered observations with SHA-256 integrity hash."""
    m = mission.lower().strip()
    f = format.lower().strip()
    if m not in ["curiosity", "msl", "insight"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported export mission '{mission}'. Supported missions are 'curiosity' and 'insight'."
        )
    if f not in ["json", "csv"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported export format '{format}'. Supported formats are 'json' and 'csv'."
        )
    records = data_loader.get_curiosity_records() if m in ["curiosity", "msl"] else data_loader.get_insight_records()
    
    if f == "csv":
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
                "Content-Disposition": f"attachment; filename={m}_mars_telemetry.csv",
                "X-Dataset-SHA256": sha256
            }
        )
        return response
    else:
        content_str = json.dumps(records, indent=2)
        sha256 = hashlib.sha256(content_str.encode("utf-8")).hexdigest()
        return JSONResponse(
            content={"metadata": {"mission": m, "count": len(records), "sha256": sha256}, "data": records}
        )
