"""
Dual-Mode Anomaly Intelligence Engine.
Combines Robust Z-Score (Median Absolute Deviation) for univariate outliers,
and Isolation Forest for multivariate joint environmental anomaly detection.
Generates the Anomaly Timeline and Event Replay reconstructions (T-12 to T+12).
Fulfills Directive 18, 19, 20, 21, 60.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_univariate_anomalies(
    records: List[Dict[str, Any]], 
    variable: str = "air_temp_max_c",
    threshold: float = 3.0
) -> List[Dict[str, Any]]:
    """
    Detects univariate anomalies using Modified Z-Score based on Median Absolute Deviation (MAD).
    Robust to heavy-tailed and non-Gaussian planetary distributions.
    """
    vals = [r.get(variable) for r in records if r.get(variable) is not None]
    if len(vals) < 15:
        return []

    arr = np.array(vals)
    med = np.median(arr)
    mad = np.median(np.abs(arr - med))
    if mad == 0:
        mad = 1e-6  # Prevent division by zero

    anomalies = []
    for r in records:
        v = r.get(variable)
        if v is not None:
            # 0.6745 factor normalizes MAD to standard deviation for normal distributions
            mod_z = 0.6745 * (v - med) / mad
            if abs(mod_z) >= threshold:
                severity = "EXTREME" if abs(mod_z) >= 4.5 else ("HIGH" if abs(mod_z) >= 3.5 else "MODERATE")
                anomalies.append({
                    "sol": r.get("sol"),
                    "terrestrial_date": r.get("terrestrial_date"),
                    "variable": variable,
                    "observed_value": v,
                    "median_reference": round(float(med), 2),
                    "modified_z_score": round(float(mod_z), 2),
                    "severity": severity,
                    "algorithm": "Robust Z-Score (Median Absolute Deviation)"
                })

    return anomalies

def detect_multivariate_anomalies(
    records: List[Dict[str, Any]],
    contamination: float = 0.025
) -> List[Dict[str, Any]]:
    """
    Multivariate Anomaly Detection using Isolation Forest.
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

    X = sub_df[cols].values
    iso_forest = IsolationForest(
        n_estimators=120, 
        contamination=contamination, 
        random_state=42,
        n_jobs=1
    )
    iso_forest.fit(X)
    
    # Anomaly score: lower score means more anomalous. Invert for standard 0-100 severity
    scores = iso_forest.score_samples(X)
    preds = iso_forest.predict(X)  # -1 indicates anomaly

    anomalies = []
    # Normalize score between 0 and 100
    min_s, max_s = np.min(scores), np.max(scores)
    
    for idx, (pred, score) in enumerate(zip(preds, scores)):
        if pred == -1:
            row = sub_df.iloc[idx]
            # Convert raw score to 0-100 anomaly intensity
            anomaly_intensity = round(float((max_s - score) / (max_s - min_s + 1e-9) * 100), 1)
            
            # Determine primary contributing factor
            factors = []
            if row["temp_amplitude_c"] < 35.0:
                factors.append("Drastic Diurnal Temperature Collapse (Dust Thermal Blanket)")
            elif row["temp_amplitude_c"] > 70.0:
                factors.append("Extreme Diurnal Temperature Range (Clear Atmospheric Radiative Forcing)")
            if row["pressure_pa"] > 950.0:
                factors.append("Atmospheric Pressure Peak (CO2 Polar Cap Sublimation)")
            elif row["pressure_pa"] < 670.0:
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

def generate_event_replay(
    records: List[Dict[str, Any]], 
    target_sol: int,
    window_sols: int = 12
) -> Optional[Dict[str, Any]]:
    """
    Signature WOW Moment #1: Mars Environmental Event Replay.
    Reconstructs the surrounding environmental state from T - 12 Sols to T + 12 Sols.
    Provides phased scientific narrative of how the atmosphere entered and recovered from the anomaly.
    """
    df = pd.DataFrame(records)
    if "sol" not in df.columns:
        return None

    event_row = df[df["sol"] == target_sol]
    if event_row.empty:
        return None
    event_data = event_row.iloc[0].to_dict()

    start_sol = target_sol - window_sols
    end_sol = target_sol + window_sols
    window_df = df[(df["sol"] >= start_sol) & (df["sol"] <= end_sol)].sort_values("sol")

    timeline_points = []
    for _, r in window_df.iterrows():
        timeline_points.append({
            "sol": int(r["sol"]),
            "terrestrial_date": str(r.get("terrestrial_date", "")),
            "offset_sols": int(r["sol"] - target_sol),
            "air_temp_max_c": r.get("air_temp_max_c"),
            "air_temp_min_c": r.get("air_temp_min_c"),
            "temp_amplitude_c": r.get("temp_amplitude_c"),
            "pressure_pa": r.get("pressure_pa"),
            "is_anomaly_center": bool(r["sol"] == target_sol)
        })

    # Scientific Event Reconstruction Narrative
    # Check if this is a dust-storm related event (temperature amplitude reduction)
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
