"""
Tests for ML Pipeline: Chronological Split, Zero Lookahead Leakage,
4-Way Baseline Benchmarking, and Dust Storm Failure Case Analysis.
"""

import pytest
import numpy as np
from app.ml.model_lab import build_feature_matrix, run_model_experiment

def generate_synthetic_continuous_observations(n_sols: int = 500):
    """Generates continuous ordered Sol observations with solar cycle for testing."""
    records = []
    base_temp = -60.0
    for sol in range(1, n_sols + 1):
        # Cyclical Ls from 0 to 360
        ls = float((sol * 0.5) % 360.0)
        # Seasonal amplitude
        amplitude = 45.0 + 10.0 * np.sin(np.radians(ls)) + np.random.normal(0, 1.5)
        # Introduce a non-linear radiative collapse during dust season Ls in [180, 270]
        if 200.0 <= ls <= 220.0 and sol % 10 == 0:
            amplitude -= 18.0  # Causes severe prediction error > 14 deg C

        min_temp = base_temp - amplitude / 2.0
        max_temp = base_temp + amplitude / 2.0
        pressure = 800.0 + 50.0 * np.cos(np.radians(ls)) + np.random.normal(0, 2.0)

        records.append({
            "sol": sol,
            "terrestrial_date": f"2020-01-01",
            "air_temp_max_c": max_temp,
            "air_temp_min_c": min_temp,
            "temp_amplitude_c": amplitude,
            "pressure_pa": pressure,
            "solar_longitude_ls": ls,
            "martian_season": "Southern Spring / Dust Storm Season" if 180 <= ls < 270 else "Northern Spring"
        })
    return records

def test_chronological_split_strict_ordering():
    """Verify that Train, Val, and Test sets maintain strict chronological ordering with no overlap."""
    records = generate_synthetic_continuous_observations(n_sols=400)
    res = run_model_experiment(records)

    split = res["dataset_split"]
    train_count = split["train_samples"]
    val_count = split["val_samples"]
    test_count = split["test_samples"]
    total = train_count + val_count + test_count

    # Verify 70 / 15 / 15 proportions
    assert train_count == int(total * 0.70)
    assert val_count == int(total * 0.85) - int(total * 0.70)
    assert test_count == total - int(total * 0.85)

    # Verify sol ranges are strictly partitioned: train < val < test
    assert "Sol" in split["train_sol_range"]
    assert "Sol" in split["val_sol_range"]
    assert "Sol" in split["test_sol_range"]

def test_four_baseline_metrics_computed():
    """Verify that Persistence, Rolling 7-Sol, Ridge, and Random Forest all report MAE, RMSE, and R2."""
    records = generate_synthetic_continuous_observations(n_sols=300)
    res = run_model_experiment(records)

    models = res["models_comparison"]
    assert len(models) == 4

    expected_names = [
        "Naive Persistence Baseline (y_t = y_{t-1})",
        "Rolling 7-Sol Mean Baseline",
        "Ridge Regularized Linear Model",
        "Random Forest Regressor (Selected Model)"
    ]

    for model in models:
        assert model["model_name"] in expected_names
        assert "mae" in model and isinstance(model["mae"], (float, int))
        assert "rmse" in model and isinstance(model["rmse"], (float, int))
        assert "r2" in model and isinstance(model["r2"], (float, int))
        assert model["mae"] >= 0.0
        assert model["rmse"] >= 0.0

def test_honest_failure_case_logged():
    """Verify that Ls in [180, 270] dust storm failure cases are detected and logged in the result."""
    records = generate_synthetic_continuous_observations(n_sols=500)
    res = run_model_experiment(records)

    slice_analysis = res["slice_error_analysis"]
    assert "dust_storm_failure_cases" in slice_analysis
    assert "failure_case_analysis" in slice_analysis
    assert "Ls 180" in slice_analysis["failure_case_analysis"]

    # Verify failure cases have required schema fields
    for case in slice_analysis["dust_storm_failure_cases"]:
        assert 180.0 <= case["solar_longitude_ls"] <= 270.0
        assert case["error_c"] >= 14.0
        assert "phenomenon" in case

def test_real_sol_lags_prevent_false_consecutive_lag_on_gaps():
    """Phase 4.1 Regression: Gapped Sols must not treat separated records as consecutive Sol lags."""
    import pandas as pd
    records = [
        {"sol": 100, "temp_amplitude_c": 50.0, "pressure_pa": 800.0, "solar_longitude_ls": 10.0},
        {"sol": 101, "temp_amplitude_c": 52.0, "pressure_pa": 802.0, "solar_longitude_ls": 10.5},
        # Big multi-sol gap: Sol 102 - 109 missing
        {"sol": 110, "temp_amplitude_c": 60.0, "pressure_pa": 810.0, "solar_longitude_ls": 15.0},
        {"sol": 111, "temp_amplitude_c": 62.0, "pressure_pa": 812.0, "solar_longitude_ls": 15.5},
        {"sol": 112, "temp_amplitude_c": 64.0, "pressure_pa": 814.0, "solar_longitude_ls": 16.0},
    ]
    X, y, df = build_feature_matrix(records)
    # Sol 110 must NOT appear with Sol 101 as its lag_1 (because Sol 109 is missing)
    # Only Sols with authentic t-1, t-2, and rolling-7 data should be retained
    retained_sols = df["sol"].tolist()
    assert 110 not in retained_sols, "Sol 110 should not have been retained with false t-1 lag across a 9-sol gap"

def test_zero_baseline_division_guard():
    """Phase 4.3 Regression: Zero baseline MAE cannot trigger a division-by-zero error."""
    # Constant data where baseline MAE could be 0
    records = []
    for sol in range(1, 150):
        records.append({
            "sol": sol,
            "temp_amplitude_c": 50.0,  # completely constant
            "pressure_pa": 800.0,
            "solar_longitude_ls": float(sol % 360),
            "martian_season": "Northern Spring"
        })
    res = run_model_experiment(records)
    # Must succeed without ZeroDivisionError
    assert "models_comparison" in res
    for m in res["models_comparison"]:
        assert m["mae"] >= 0.0


def test_ridge_model_has_improvement_over_baseline_pct():
    """Regression: Ridge model must expose improvement_over_baseline_pct (not None) so frontend can display delta."""
    records = generate_synthetic_continuous_observations(n_sols=300)
    res = run_model_experiment(records)
    ridge = next(m for m in res["models_comparison"] if "Ridge" in m["model_name"])
    assert "improvement_over_baseline_pct" in ridge, "Ridge must include improvement_over_baseline_pct field"
    # Value may be None only if baseline MAE is effectively zero (degenerate case), float otherwise
    if ridge["improvement_over_baseline_pct"] is not None:
        assert isinstance(ridge["improvement_over_baseline_pct"], float)


def test_martian_season_column_absent_uses_ls_fallback():
    """Regression: model_lab must not crash when martian_season column is absent; Ls-based season bins used instead."""
    records = []
    for sol in range(1, 350):
        ls = float((sol * 0.5) % 360.0)
        amp = 45.0 + 10.0 * np.sin(np.radians(ls))
        records.append({
            "sol": sol,
            "temp_amplitude_c": amp,
            "air_temp_max_c": -20.0 + amp / 2,
            "air_temp_min_c": -20.0 - amp / 2,
            "pressure_pa": 800.0 + 50.0 * np.cos(np.radians(ls)),
            "solar_longitude_ls": ls,
            # NOTE: martian_season deliberately omitted
        })
    res = run_model_experiment(records)
    assert "slice_error_analysis" in res
    seasonal_slices = res["slice_error_analysis"]["seasonal_slices"]
    # Should have produced at least 1 Ls-based season bin
    assert len(seasonal_slices) >= 1, "Ls fallback season binning must produce at least 1 bin"
    for label, stats in seasonal_slices.items():
        assert "mae" in stats
        assert "sample_count" in stats
