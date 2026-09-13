import pytest
from app.analytics.challenge_index import calculate_meci, simulate_scenario

def test_meci_bounds_and_structure():
    meci = calculate_meci(
        temp_amplitude_c=55.0,
        pressure_pa=820.0,
        pressure_rate_of_change=1.5,
        solar_longitude_ls=90.0,
        anomaly_intensity=20.0
    )
    assert 0.0 <= meci["index_score"] <= 100.0
    assert meci["classification"] in ["LOW", "MODERATE", "HIGH", "EXTREME"]
    assert "factor_breakdown" in meci
    assert "thermal_stress" in meci["factor_breakdown"]
    assert "barometric_instability" in meci["factor_breakdown"]
    assert "anomaly_intensity" in meci["factor_breakdown"]
    assert "seasonal_dust_forcing" in meci["factor_breakdown"]

def test_meci_dust_season_increase():
    # Clear season (Ls = 60)
    meci_clear = calculate_meci(
        temp_amplitude_c=55.0,
        pressure_pa=820.0,
        pressure_rate_of_change=1.0,
        solar_longitude_ls=60.0
    )
    # Perihelion dust storm window (Ls = 250)
    meci_dust = calculate_meci(
        temp_amplitude_c=55.0,
        pressure_pa=820.0,
        pressure_rate_of_change=1.0,
        solar_longitude_ls=250.0
    )
    assert meci_dust["index_score"] > meci_clear["index_score"]

def test_simulate_scenario():
    base_meci = calculate_meci(
        temp_amplitude_c=50.0,
        pressure_pa=800.0,
        pressure_rate_of_change=1.0,
        solar_longitude_ls=70.0,
        anomaly_intensity=10.0
    )
    sim = simulate_scenario(
        base_meci=base_meci,
        temp_variability_multiplier=1.5,
        pressure_drop_pa=20.0,
        inject_dust_storm=True
    )
    assert sim["status"] == "SIMULATED ANALYTICAL SCENARIO"
    assert sim["simulated_meci"] > base_meci["index_score"]
    assert sim["delta"] > 0
