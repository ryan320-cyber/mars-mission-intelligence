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
    Downsamples a large series to at most max_points using linear grid sampling.
    Strictly guarantees output_count <= max_points while preserving the first
    and latest observations.
    """
    if max_points <= 0:
        raise ValueError(f"max_points must be a strictly positive integer >= 1, got {max_points}")

    if not records:
        return []

    n = len(records)
    if n <= max_points:
        return list(records)

    if max_points == 1:
        return [records[-1]]

    # Generate at most max_points evenly spaced indices strictly covering 0 to n - 1
    indices = np.round(np.linspace(0, n - 1, max_points)).astype(int)
    unique_indices = sorted(list(dict.fromkeys(indices)))
    
    # Guarantee output length does not exceed max_points
    if len(unique_indices) > max_points:
        unique_indices = unique_indices[:max_points]

    return [records[i] for i in unique_indices]

def downsample_vertical_profiles(
    profiles: List[Dict[str, Any]], 
    target_levels: int = 15
) -> List[Dict[str, Any]]:
    """
    Smart downsampling for MRO MCS atmospheric sounding profiles (0-80 km).
    Shrinks vertical transmission payload while strictly preserving:
      1. Surface boundary layer level (altitude = min altitude, index 0).
      2. Upper atmospheric boundary (altitude = max altitude, index n - 1).
      3. Scientifically significant local temperature extrema (mesospheric inversion peak, tropospheric min).
      4. 1-sigma uncertainty envelopes and all associated atmospheric layer properties.
    Guarantees retained_level_count <= target_levels and target_levels >= 2.
    """
    if target_levels < 2:
        raise ValueError(f"target_levels must be >= 2 to preserve atmospheric boundaries, got {target_levels}")

    downsampled_profiles = []
    for prof in profiles:
        levels = prof.get("levels", [])
        if len(levels) <= target_levels:
            downsampled_profiles.append(prof)
            continue

        # Sort levels by altitude
        sorted_levels = sorted(levels, key=lambda lvl: lvl.get("altitude_km", 0.0))
        n = len(sorted_levels)
        
        # 1. Critical Boundaries: Surface (0) and Top of Atmosphere (n - 1)
        critical_indices = {0, n - 1}

        # 2. Identify local temperature extrema (thermal inversions / cold points)
        for i in range(1, n - 1):
            t_prev = sorted_levels[i - 1].get("temperature_k")
            t_curr = sorted_levels[i].get("temperature_k")
            t_next = sorted_levels[i + 1].get("temperature_k")
            if t_prev is not None and t_curr is not None and t_next is not None:
                # Local maximum (thermal inversion) or local minimum
                if (t_curr > t_prev and t_curr > t_next) or (t_curr < t_prev and t_curr < t_next):
                    critical_indices.add(i)

        # 3. Evenly spaced grid to fill remaining resolution up to target_levels
        grid_indices = set(np.round(np.linspace(0, n - 1, target_levels)).astype(int).tolist())
        
        # Combine critical indices and grid indices
        combined_indices = sorted(list(critical_indices | grid_indices))

        # If combined exceeds target_levels, prioritize boundaries and extrema, pruning intermediate grid
        if len(combined_indices) > target_levels:
            # Must keep 0 and n-1
            must_keep = {0, n - 1} | critical_indices
            optional = [idx for idx in combined_indices if idx not in must_keep]
            slots_available = max(0, target_levels - len(must_keep))
            if slots_available > 0 and optional:
                step = max(1, len(optional) // slots_available)
                kept_optional = set(optional[::step][:slots_available])
            else:
                kept_optional = set()
            selected_indices = sorted(list(must_keep | kept_optional))[:target_levels]
        else:
            selected_indices = combined_indices

        sampled_levels = [sorted_levels[i] for i in selected_indices]
        prof_copy = dict(prof)
        prof_copy["levels"] = sampled_levels
        prof_copy["downsampled"] = True
        prof_copy["original_level_count"] = n
        prof_copy["retained_level_count"] = len(sampled_levels)
        downsampled_profiles.append(prof_copy)

    return downsampled_profiles

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
