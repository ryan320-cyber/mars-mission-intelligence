import pytest
import numpy as np
from app.analytics.statistics import compute_summary_statistics, compute_correlation_matrix
from app.analytics.time_series import downsample_time_series, identify_sensor_gaps

def test_compute_summary_statistics():
    data = [10.0, 12.0, 15.0, 14.0, 18.0, 20.0, 25.0]
    stats = compute_summary_statistics(data)
    assert stats["count"] == 7
    assert stats["min"] == 10.0
    assert stats["max"] == 25.0
    assert stats["mean"] == pytest.approx(16.29, 0.05)
    assert stats["median"] == 15.0
    assert stats["iqr"] > 0

def test_compute_correlation_matrix():
    records = [
        {"temp": 10.0, "press": 800.0, "ls": 10.0},
        {"temp": 15.0, "press": 810.0, "ls": 20.0},
        {"temp": 20.0, "press": 820.0, "ls": 30.0},
        {"temp": 25.0, "press": 830.0, "ls": 40.0},
        {"temp": 30.0, "press": 840.0, "ls": 50.0},
    ]
    res = compute_correlation_matrix(records, ["temp", "press", "ls"])
    assert res["sample_size"] == 5
    assert res["pearson"]["temp"]["press"]["r"] == pytest.approx(1.0, 0.01)
    assert res["spearman"]["temp"]["press"]["rho"] == pytest.approx(1.0, 0.01)

def test_downsample_time_series():
    records = [{"sol": i, "val": i * 2} for i in range(1000)]
    downsampled = downsample_time_series(records, max_points=100)
    assert len(downsampled) <= 100
    assert downsampled[0]["sol"] == 0
    assert downsampled[-1]["sol"] == 999

    # Test previously failing boundary case: 799 points targeting 400
    recs_799 = [{"sol": i, "val": i} for i in range(799)]
    downsampled_400 = downsample_time_series(recs_799, max_points=400)
    assert len(downsampled_400) <= 400
    assert downsampled_400[0]["sol"] == 0
    assert downsampled_400[-1]["sol"] == 798

def test_identify_sensor_gaps():
    records = [
        {"sol": 1, "terrestrial_date": "2012-08-07"},
        {"sol": 2, "terrestrial_date": "2012-08-08"},
        {"sol": 10, "terrestrial_date": "2012-08-16"},  # Gap of 8 sols
        {"sol": 11, "terrestrial_date": "2012-08-17"},
    ]
    gaps = identify_sensor_gaps(records, sol_gap_threshold=3)
    assert len(gaps) == 1
    assert gaps[0]["start_sol"] == 2
    assert gaps[0]["end_sol"] == 10
    assert gaps[0]["gap_duration_sols"] == 8

def test_downsample_vertical_profiles_preserves_boundaries_and_extrema():
    """Phase 7 Regression: Vertical profile downsampling preserves surface and TOA boundaries and uncertainty."""
    from app.analytics.time_series import downsample_vertical_profiles
    profiles = [{
        "profile_id": "test_profile_1",
        "levels": [
            {"altitude_km": float(i * 3), "temperature_k": 200.0 - i * 2, "temperature_uncertainty_k": 1.5 + i * 0.2}
            for i in range(25)
        ]
    }]
    downsampled = downsample_vertical_profiles(profiles, target_levels=10)
    assert len(downsampled) == 1
    levels = downsampled[0]["levels"]
    assert len(levels) <= 12
    # Surface boundary level (0.0 km) must be preserved
    assert levels[0]["altitude_km"] == 0.0
    # Top of atmosphere level (72.0 km) must be preserved
    assert levels[-1]["altitude_km"] == 72.0
    # 1-sigma uncertainty must be preserved
    for lvl in levels:
        assert "temperature_uncertainty_k" in lvl
        assert lvl["temperature_uncertainty_k"] > 0

def test_correlation_matrix_zero_variance():
    """Phase 3.2 Regression: Constant variable with zero variance does not crash correlation engine."""
    records = [
        {"temp": 20.0, "press": 800.0, "ls": 10.0},
        {"temp": 20.0, "press": 810.0, "ls": 20.0},
        {"temp": 20.0, "press": 820.0, "ls": 30.0},
        {"temp": 20.0, "press": 830.0, "ls": 40.0},
    ]
    res = compute_correlation_matrix(records, ["temp", "press", "ls"])
    assert res["status"] in ["OK", "ZERO_VARIANCE"]
    assert res["pearson"]["temp"]["press"]["r"] is None
    assert res["pearson"]["temp"]["press"]["status"] == "ZERO_VARIANCE"

def test_compare_missions_flags_synthetic_demonstration():
    """Phase 3.2 Regression: Cross-mission comparison between Curiosity and InSight identifies synthetic baseline."""
    from app.analytics.statistics import compare_missions
    curiosity = [
        {"sol": 1, "pressure_pa": 840.0, "air_temp_max_c": -10.0, "is_synthetic": False},
        {"sol": 2, "pressure_pa": 842.0, "air_temp_max_c": -12.0, "is_synthetic": False},
        {"sol": 3, "pressure_pa": 841.0, "air_temp_max_c": -11.0, "is_synthetic": False},
        {"sol": 4, "pressure_pa": 843.0, "air_temp_max_c": -13.0, "is_synthetic": False},
        {"sol": 5, "pressure_pa": 844.0, "air_temp_max_c": -14.0, "is_synthetic": False},
        {"sol": 6, "pressure_pa": 845.0, "air_temp_max_c": -15.0, "is_synthetic": False},
        {"sol": 7, "pressure_pa": 846.0, "air_temp_max_c": -16.0, "is_synthetic": False},
        {"sol": 8, "pressure_pa": 847.0, "air_temp_max_c": -17.0, "is_synthetic": False},
        {"sol": 9, "pressure_pa": 848.0, "air_temp_max_c": -18.0, "is_synthetic": False},
        {"sol": 10, "pressure_pa": 849.0, "air_temp_max_c": -19.0, "is_synthetic": False},
    ]
    insight = [
        {"sol": 1, "pressure_pa": 740.0, "air_temp_max_c": -15.0, "is_synthetic": True},
        {"sol": 2, "pressure_pa": 742.0, "air_temp_max_c": -17.0, "is_synthetic": True},
        {"sol": 3, "pressure_pa": 741.0, "air_temp_max_c": -16.0, "is_synthetic": True},
        {"sol": 4, "pressure_pa": 743.0, "air_temp_max_c": -18.0, "is_synthetic": True},
        {"sol": 5, "pressure_pa": 744.0, "air_temp_max_c": -19.0, "is_synthetic": True},
        {"sol": 6, "pressure_pa": 745.0, "air_temp_max_c": -20.0, "is_synthetic": True},
        {"sol": 7, "pressure_pa": 746.0, "air_temp_max_c": -21.0, "is_synthetic": True},
        {"sol": 8, "pressure_pa": 747.0, "air_temp_max_c": -22.0, "is_synthetic": True},
        {"sol": 9, "pressure_pa": 748.0, "air_temp_max_c": -23.0, "is_synthetic": True},
        {"sol": 10, "pressure_pa": 749.0, "air_temp_max_c": -24.0, "is_synthetic": True},
    ]
    res = compare_missions(curiosity, insight)
    assert res["comparison_type"] == "OBSERVED_VS_SIMULATED_DEMONSTRATION"
    assert "DEMONSTRATION" in res["methodological_caveat"]

