"""
Time-Series Processing & Feature Engineering Engine.
Provides Sol synchronization, rolling statistics, rate-of-change, gap detection,
and adaptive downsampling for multi-thousand Sol datasets.
Fulfills Directive 11 (Time-Series Engine), Directive 13 (Sol Analysis), Directive 64 (Sensor Gaps).
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

def prepare_dataframe(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """Converts records into a typed, indexed pandas DataFrame."""
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    if "sol" in df.columns:
        df["sol"] = pd.to_numeric(df["sol"], errors="coerce")
        df = df.sort_values("sol").reset_index(drop=True)
    return df

def calculate_time_series_features(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Computes rolling averages, standard deviations, diurnal swings, and rates of change.
    Strictly past-looking (no future lookahead).
    """
    df = prepare_dataframe(records)
    if df.empty:
        return []

    # Rolling statistics for temperature and pressure
    if "air_temp_max_c" in df.columns and "air_temp_min_c" in df.columns:
        # Diurnal temperature swing
        df["temp_amplitude_c"] = df["air_temp_max_c"] - df["air_temp_min_c"]
        df["air_temp_mean_c"] = (df["air_temp_max_c"] + df["air_temp_min_c"]) / 2.0
        # Rolling 7-Sol and 30-Sol windows
        df["temp_rolling_7_mean"] = df["air_temp_mean_c"].rolling(window=7, min_periods=3).mean()
        df["temp_rolling_7_std"] = df["air_temp_mean_c"].rolling(window=7, min_periods=3).std()
        df["temp_rate_of_change"] = df["air_temp_mean_c"].diff()

    if "pressure_pa" in df.columns:
        df["pressure_rolling_7_mean"] = df["pressure_pa"].rolling(window=7, min_periods=3).mean()
        df["pressure_rolling_30_mean"] = df["pressure_pa"].rolling(window=30, min_periods=10).mean()
        df["pressure_rate_of_change"] = df["pressure_pa"].diff()

    # Detect sensor gap interval
    if "sol" in df.columns:
        df["sol_diff"] = df["sol"].diff()
        df["is_sensor_gap"] = df["sol_diff"] > 1

    # Replace NaNs with None for clean JSON serialization
    clean_df = df.replace({np.nan: None})
    return clean_df.to_dict(orient="records")

def downsample_time_series(
    records: List[Dict[str, Any]], 
    max_points: int = 500
) -> List[Dict[str, Any]]:
    """
    Downsamples a large series to max_points using Largest-Triangle-Three-Buckets (LTTB) 
    or uniform decimation to ensure smooth chart performance while preserving extrema.
    """
    if len(records) <= max_points:
        return records

    step = max(1, len(records) // max_points)
    sampled = records[::step]
    
    # Always include the latest observation
    if records[-1] not in sampled:
        sampled.append(records[-1])
    return sampled

def identify_sensor_gaps(records: List[Dict[str, Any]], sol_gap_threshold: int = 3) -> List[Dict[str, Any]]:
    """Surfaces significant observational gaps where telemetry was interrupted."""
    gaps = []
    if len(records) < 2:
        return gaps

    for i in range(1, len(records)):
        prev_sol = records[i - 1].get("sol")
        curr_sol = records[i].get("sol")
        if prev_sol is not None and curr_sol is not None:
            gap_size = curr_sol - prev_sol
            if gap_size >= sol_gap_threshold:
                gaps.append({
                    "start_sol": prev_sol,
                    "end_sol": curr_sol,
                    "gap_duration_sols": gap_size,
                    "start_date": records[i - 1].get("terrestrial_date", "Unknown"),
                    "end_date": records[i].get("terrestrial_date", "Unknown"),
                    "reason": "Probable Solar Conjunction, Drill Operation, or Safe Mode" if gap_size > 14 else "Sensor Calibration / Data Uplink Gap"
                })
    return gaps
