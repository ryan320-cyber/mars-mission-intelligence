"""
Martian Environmental Challenge Index (MECI) & Scenario Analysis Engine.
Transparent, reproducible project-defined analytical index (0 - 100)
reflecting thermal, barometric, and seasonal environmental challenges.
Fulfills Directive 29, 30, 31, 32.
"""

from typing import Dict, Any, List, Optional
import numpy as np

def calculate_meci(
    temp_amplitude_c: Optional[float],
    pressure_pa: Optional[float],
    pressure_rate_of_change: Optional[float],
    solar_longitude_ls: Optional[float],
    anomaly_intensity: float = 0.0,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Computes the Martian Environmental Challenge Index (0 - 100).
    
    Formula:
        MECI = w1 * F_thermal + w2 * F_pressure + w3 * F_anomaly + w4 * F_season
    
    Default weights:
        - Thermal Stress (Diurnal swing fatigue): 0.35
        - Barometric Instability (Atmospheric density fluctuation): 0.25
        - Anomaly Intensity (Multivariate abnormality): 0.25
        - Seasonal Dust Forcing (Perihelion dust window): 0.15
    """
    if weights is None:
        weights = {
            "thermal_stress": 0.35,
            "barometric_instability": 0.25,
            "anomaly_intensity": 0.25,
            "seasonal_forcing": 0.15
        }

    # 1. Thermal Stress: Mars diurnal swings range between 20°C (during heavy dust storms) and 80°C (clear skies)
    # High diurnal swing strains mechanical joints, batteries, and solar arrays
    amp = temp_amplitude_c if temp_amplitude_c is not None else 52.0
    f_thermal = float(np.clip((amp / 75.0) * 100.0, 0.0, 100.0))

    # 2. Barometric Instability: Rapid pressure swings indicate atmospheric gravity waves or tidal surges
    # Surface pressure typically changes < 5 Pa/day; changes > 15 Pa/day indicate sharp barometric turbulence
    dp = abs(pressure_rate_of_change) if pressure_rate_of_change is not None else 2.5
    f_pressure = float(np.clip((dp / 18.0) * 100.0, 0.0, 100.0))

    # 3. Anomaly Intensity: Derived directly from Isolation Forest / Robust Z-score (0 - 100)
    f_anomaly = float(np.clip(anomaly_intensity, 0.0, 100.0))

    # 4. Seasonal Forcing: Solar Longitude Ls between 180° and 320° is the classic Martian Dust Storm Season
    # Perihelion occurs near Ls 251°, causing maximum solar heating and planetary dust lifting
    if solar_longitude_ls is not None:
        ls_norm = solar_longitude_ls % 360.0
        if 180.0 <= ls_norm <= 320.0:
            # Distance from peak dust window (Ls ~250°)
            dist = abs(ls_norm - 250.0)
            f_season = float(np.clip(100.0 - (dist * 1.2), 30.0, 100.0))
        else:
            f_season = 20.0
    else:
        f_season = 35.0

    # Weighted Composite Score
    composite_score = (
        weights["thermal_stress"] * f_thermal +
        weights["barometric_instability"] * f_pressure +
        weights["anomaly_intensity"] * f_anomaly +
        weights["seasonal_forcing"] * f_season
    )
    score_rounded = round(float(np.clip(composite_score, 0.0, 100.0)), 1)

    # Risk Tier Classification
    if score_rounded < 30.0:
        tier = "LOW"
        tier_color = "emerald"
    elif score_rounded < 60.0:
        tier = "MODERATE"
        tier_color = "amber"
    elif score_rounded < 80.0:
        tier = "HIGH"
        tier_color = "warning"
    else:
        tier = "EXTREME"
        tier_color = "danger"

    return {
        "index_score": score_rounded,
        "classification": tier,
        "classification_color": tier_color,
        "formula": "MECI = 0.35 * F_thermal + 0.25 * F_pressure + 0.25 * F_anomaly + 0.15 * F_season",
        "factor_breakdown": {
            "thermal_stress": {
                "score": round(f_thermal, 1),
                "weight": weights["thermal_stress"],
                "metric": f"Diurnal Swing: {amp:.1f} °C",
                "rationale": "Large diurnal amplitude induces thermal cycling fatigue on solar arrays and actuators."
            },
            "barometric_instability": {
                "score": round(f_pressure, 1),
                "weight": weights["barometric_instability"],
                "metric": f"Pressure Delta: {dp:.1f} Pa/Sol",
                "rationale": "Dynamic pressure shifts indicate boundary layer mixing and atmospheric wave passage."
            },
            "anomaly_intensity": {
                "score": round(f_anomaly, 1),
                "weight": weights["anomaly_intensity"],
                "metric": f"Isolation Forest Severity: {f_anomaly:.1f}/100",
                "rationale": "Statistical distance of joint planetary state from historic baseline."
            },
            "seasonal_dust_forcing": {
                "score": round(f_season, 1),
                "weight": weights["seasonal_forcing"],
                "metric": f"Solar Longitude (Ls): {solar_longitude_ls if solar_longitude_ls is not None else 'N/A'}°",
                "rationale": "Proximity to perihelion dust storm window (Ls 180° - 320°)."
            }
        },
        "disclaimer": (
            "PROJECT ANALYTICAL INDEX: The Martian Environmental Challenge Index is a transparent "
            "engineering analysis score designed to quantify environmental volatility. It does not represent "
            "official NASA mission safety or astronaut survival thresholds."
        )
    }

def simulate_scenario(
    base_meci: Dict[str, Any],
    temp_variability_multiplier: float = 1.0,
    pressure_drop_pa: float = 0.0,
    inject_dust_storm: bool = False
) -> Dict[str, Any]:
    """
    Simulates a hypothetical analytical 'What-If' scenario.
    Fulfills Directive 32 with explicit SIMULATED ANALYTICAL SCENARIO labeling.
    """
    factors = base_meci["factor_breakdown"]
    
    # Adjust factors based on hypothetical parameters
    f_thermal = min(100.0, factors["thermal_stress"]["score"] * temp_variability_multiplier)
    f_pressure = min(100.0, factors["barometric_instability"]["score"] + (abs(pressure_drop_pa) * 2.0))
    f_season = 95.0 if inject_dust_storm else factors["seasonal_dust_forcing"]["score"]
    f_anomaly = 90.0 if inject_dust_storm else factors["anomaly_intensity"]["score"]

    sim_score = (
        0.35 * f_thermal +
        0.25 * f_pressure +
        0.25 * f_anomaly +
        0.15 * f_season
    )
    sim_score = round(float(np.clip(sim_score, 0.0, 100.0)), 1)
    
    delta = round(sim_score - base_meci["index_score"], 1)

    return {
        "status": "SIMULATED ANALYTICAL SCENARIO",
        "scenario_parameters": {
            "temp_variability_multiplier": temp_variability_multiplier,
            "hypothetical_pressure_drop_pa": pressure_drop_pa,
            "dust_storm_active": inject_dust_storm
        },
        "baseline_meci": base_meci["index_score"],
        "simulated_meci": sim_score,
        "delta": delta,
        "delta_description": f"{'+' if delta > 0 else ''}{delta} points vs observed baseline",
        "warning": "This output is a mathematical simulation for educational sensitivity analysis and is not a forecast."
    }
