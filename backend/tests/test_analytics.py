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
    assert len(downsampled) <= 105
    assert downsampled[0]["sol"] == 0
    assert downsampled[-1]["sol"] == 999

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
