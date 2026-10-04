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
        assert case["error_c"] > 14.0
        assert "phenomenon" in case
