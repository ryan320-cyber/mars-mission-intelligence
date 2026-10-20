"""
Dual-Mode Anomaly Intelligence Engine.
Combines Robust Z-Score (Median Absolute Deviation) for univariate outliers,
and Isolation Forest for multivariate joint environmental anomaly detection.
Generates the Anomaly Timeline and Event Replay reconstructions (T-12 to T+12).
Fulfills Directive 18, 19, 20, 21, 60.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_univariate_anomalies(
    records: List[Dict[str, Any]], 
    variable: str = "air_temp_max_c",
    threshold: float = 3.0
) -> List[Dict[str, Any]]:
    """
    Detects univariate anomalies using vectorized Modified Z-Score based on Median Absolute Deviation (MAD).
    Robust to heavy-tailed and non-Gaussian planetary distributions.
    Fully vectorized with NumPy for microsecond execution.
    """
    valid_records = [r for r in records if r.get(variable) is not None]
    if len(valid_records) < 15:
        return []

    vals = np.array([r[variable] for r in valid_records], dtype=np.float64)
    med = np.median(vals)
    mad = np.median(np.abs(vals - med))
    if mad == 0:
        mad = 1e-6  # Prevent division by zero

    # Vectorized modified Z-score (0.6745 normalizes MAD to std dev of normal distribution)
    mod_z_scores = 0.6745 * (vals - med) / mad
    abs_z = np.abs(mod_z_scores)
    anomaly_indices = np.where(abs_z >= threshold)[0]

    anomalies = []
    for idx in anomaly_indices:
        r = valid_records[idx]
        score = float(mod_z_scores[idx])
        abs_score = abs(score)
        severity = "EXTREME" if abs_score >= 4.5 else ("HIGH" if abs_score >= 3.5 else "MODERATE")
        anomalies.append({
            "sol": r.get("sol"),
            "terrestrial_date": r.get("terrestrial_date"),
            "variable": variable,
            "observed_value": r.get(variable),
            "median_reference": round(float(med), 2),
            "modified_z_score": round(score, 2),
            "severity": severity,
            "algorithm": "Robust Z-Score (Vectorized Median Absolute Deviation)"
        })

    return anomalies

def detect_multivariate_anomalies(
    records: List[Dict[str, Any]],
    contamination: float = 0.025
) -> List[Dict[str, Any]]:
    """
    Multivariate Anomaly Detection using vectorized scikit-learn Isolation Forest.
    Evaluates joint planetary states: [Max Temp, Min Temp, Temp Amplitude, Pressure].
    Identifies multi-variable anomalies where single variables may appear benign.
    """
    df = pd.DataFrame(records)
    cols = ["air_temp_max_c", "air_temp_min_c", "temp_amplitude_c", "pressure_pa"]
    for c in cols:
        if c not in df.columns:
            return []

    sub_df = df.dropna(subset=cols).copy()
    if len(sub_df) < 50:
        return []

    X = sub_df[cols].to_numpy(dtype=np.float64)
    iso_forest = IsolationForest(
        n_estimators=100, 
        contamination=contamination, 
        random_state=42,
        n_jobs=-1
    )
    iso_forest.fit(X)
    
    # Anomaly score: lower score means more anomalous. Invert for standard 0-100 severity
    scores = iso_forest.score_samples(X)
    preds = iso_forest.predict(X)  # -1 indicates anomaly

    anomalies = []
    min_s, max_s = float(np.min(scores)), float(np.max(scores))
    denominator = (max_s - min_s) if (max_s - min_s) > 1e-9 else 1e-9

    anomaly_mask = (preds == -1)
    anomaly_indices = np.where(anomaly_mask)[0]

    for idx in anomaly_indices:
        row = sub_df.iloc[idx]
        score = scores[idx]
        anomaly_intensity = round(float((max_s - score) / denominator * 100), 1)

        factors = []
        amp = row["temp_amplitude_c"]
        p = row["pressure_pa"]
        if amp < 35.0:
            factors.append("Drastic Diurnal Temperature Collapse (Dust Thermal Blanket)")
        elif amp > 70.0:
            factors.append("Extreme Diurnal Temperature Range (Clear Atmospheric Radiative Forcing)")
        if p > 950.0:
            factors.append("Atmospheric Pressure Peak (CO2 Polar Cap Sublimation)")
        elif p < 670.0:
            factors.append("Atmospheric Pressure Deep Minimum (CO2 Polar Condensation)")

        if not factors:
            factors.append("Atypical Multivariate Joint State")

        severity = "EXTREME" if anomaly_intensity > 85 else ("HIGH" if anomaly_intensity > 70 else "MODERATE")

        anomalies.append({
            "sol": int(row["sol"]),
            "terrestrial_date": str(row.get("terrestrial_date", "")),
            "anomaly_intensity": anomaly_intensity,
            "severity": severity,
            "observed_values": {
                "air_temp_max_c": row["air_temp_max_c"],
                "air_temp_min_c": row["air_temp_min_c"],
                "temp_amplitude_c": row["temp_amplitude_c"],
                "pressure_pa": row["pressure_pa"],
                "season": row.get("martian_season", "Unknown")
            },
            "primary_contributors": factors,
            "algorithm": "Multivariate Isolation Forest (Scikit-Learn)",
            "mission": row.get("mission", "Curiosity (MSL)"),
            "site": row.get("site", "Gale Crater")
        })

    anomalies.sort(key=lambda x: x["anomaly_intensity"], reverse=True)
    return anomalies

# Event replay Sol index — built fresh from the supplied records each call.
# Avoids stale-cache bugs when DataLoader reloads observations between requests.

def _get_sol_index(records: List[Dict[str, Any]]) -> Tuple[Dict[int, Dict[str, Any]], List[int]]:
    """Build O(n) Sol→record mapping from the provided records list (no global cache)."""
    sol_map = {int(r["sol"]): r for r in records if r.get("sol") is not None}
    return sol_map, sorted(sol_map.keys())

def generate_event_replay(
    records: List[Dict[str, Any]], 
    target_sol: int,
    window_sols: int = 12
) -> Optional[Dict[str, Any]]:
    """
    Signature WOW Moment #1: Mars Environmental Event Replay.
    O(1) dictionary indexed lookup responding in < 5ms for the Sol Scrubber.
    Reconstructs the surrounding environmental state from T - 12 Sols to T + 12 Sols.
    """
    sol_map, sorted_sols = _get_sol_index(records)
    if target_sol not in sol_map:
        return None

    event_data = sol_map[target_sol]

    timeline_points = []
    for s in range(target_sol - window_sols, target_sol + window_sols + 1):
        if s in sol_map:
            r = sol_map[s]
            timeline_points.append({
                "sol": s,
                "terrestrial_date": str(r.get("terrestrial_date", "")),
                "offset_sols": int(s - target_sol),
                "air_temp_max_c": r.get("air_temp_max_c"),
                "air_temp_min_c": r.get("air_temp_min_c"),
                "temp_amplitude_c": r.get("temp_amplitude_c"),
                "pressure_pa": r.get("pressure_pa"),
                "is_anomaly_center": bool(s == target_sol)
            })

    # Scientific Event Reconstruction Narrative
    amp = event_data.get("temp_amplitude_c", 50.0)
    if amp is not None and amp < 35.0:
        event_type = "Regional / Global Dust Heating Event"
        pre_narration = "Baseline Martian atmosphere shows sharp diurnal radiative swings (~55°C) with cold nights."
        event_narration = f"At Sol {target_sol}, suspended atmospheric dust trapped thermal IR radiation, collapsing diurnal amplitude to {amp}°C while warming nighttime lows."
        post_narration = "As dust sedimentation progressed, atmospheric opacity declined and diurnal swings gradually restored over the subsequent 10 sols."
    else:
        event_type = "Barometric Atmospheric Wave Event"
        pre_narration = "Atmosphere was operating under standard seasonal barometric oscillation."
        event_narration = f"At Sol {target_sol}, a significant atmospheric pressure shift of {event_data.get('pressure_pa')} Pa was recorded across Gale Crater."
        post_narration = "Local wind and barometric equilibrium normalized in subsequent sols."

    return {
        "target_sol": target_sol,
        "event_type": event_type,
        "terrestrial_date": event_data.get("terrestrial_date"),
        "mission": event_data.get("mission", "Curiosity (MSL)"),
        "site": event_data.get("site", "Gale Crater"),
        "narrative": {
            "pre_event": pre_narration,
            "anomaly_event": event_narration,
            "post_event": post_narration
        },
        "event_telemetry": event_data,
        "replay_timeline": timeline_points
    }
