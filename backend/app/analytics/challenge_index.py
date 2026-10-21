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

    # Do not turn absent observations into plausible-looking measured values.
    if temp_amplitude_c is None or pressure_pa is None or solar_longitude_ls is None:
        return {
            "index_score": None,
            "classification": "UNAVAILABLE",
            "classification_color": "#64748b",
            "formula": "MECI unavailable: required telemetry is missing.",
            "factor_breakdown": {
                key: {"score": None, "weight": weight, "metric": "Unavailable: required telemetry is missing.", "rationale": "No score calculated without required observed telemetry."}
                for key, weight in {
                    "thermal_stress": weights["thermal_stress"],
                    "barometric_instability": weights["barometric_instability"],
                    "anomaly_intensity": weights["anomaly_intensity"],
                    "seasonal_dust_forcing": weights["seasonal_forcing"],
                }.items()
            },
            "disclaimer": "No MECI score is reported because required observed telemetry is unavailable.",
        }

    # 1. Thermal Stress: Mars diurnal swings range between 20°C (during heavy dust storms) and 80°C (clear skies)
    # High diurnal swing strains mechanical joints, batteries, and solar arrays
    amp = temp_amplitude_c
    f_thermal = float(np.clip((amp / 75.0) * 100.0, 0.0, 100.0))

    # 2. Barometric Instability: Rapid pressure swings indicate atmospheric gravity waves or tidal surges
    # Surface pressure typically changes < 5 Pa/day; changes > 15 Pa/day indicate sharp barometric turbulence
    dp = abs(pressure_rate_of_change) if pressure_rate_of_change is not None else 0.0
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
        tier_color = "#f59e0b"
    else:
        tier = "EXTREME"
        tier_color = "#ef4444"

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

def compute_current_meci_from_telemetry(
    curiosity_records: List[Dict[str, Any]],
    anomalies: Optional[List[Dict[str, Any]]] = None,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Authoritative single-source-of-truth service to compute current MECI from telemetry.
    Eliminates discrepancies between /api/overview, /api/challenge-index, exports, and AI.
    
    Derives:
      - temp_amplitude_c: latest observation's temp_amplitude_c
      - pressure_pa: latest observation's pressure_pa
      - pressure_rate_of_change: computed from difference between latest and prior Sol pressure:
            |P_latest - P_prior| / max(1, |Sol_latest - Sol_prior|)
      - solar_longitude_ls: latest observation's solar_longitude_ls
      - anomaly_intensity: checks if latest Sol was flagged as an anomaly in the anomaly set;
            if so, extracts its intensity; otherwise 0.0.
    """
    if not curiosity_records:
        return calculate_meci(None, None, None, None, 0.0, weights=weights)

    valid_sols = [r for r in curiosity_records if r.get("sol") is not None]
    if not valid_sols:
        return calculate_meci(None, None, None, None, 0.0, weights=weights)

    latest = valid_sols[-1]
    latest_sol = latest.get("sol")
    if latest.get("temp_amplitude_c") is None or latest.get("pressure_pa") is None or latest.get("solar_longitude_ls") is None:
        return calculate_meci(None, None, None, None, 0.0, weights=weights)

    # Compute empirical pressure rate of change from the immediate prior Sol with pressure
    p_latest = latest.get("pressure_pa")
    dp_empirical = 0.0
    if p_latest is not None and len(valid_sols) > 1:
        for prior in reversed(valid_sols[:-1]):
            p_prior = prior.get("pressure_pa")
            if p_prior is not None:
                sol_delta = max(1, abs(int(latest_sol) - int(prior.get("sol", latest_sol))))
                dp_empirical = round(abs(float(p_latest) - float(p_prior)) / sol_delta, 2)
                break

    # Compute empirical anomaly intensity for latest Sol if present in detected anomalies
    anomaly_intensity = 0.0
    if anomalies:
        for a in anomalies:
            if a.get("sol") == latest_sol:
                anomaly_intensity = float(a.get("anomaly_intensity", a.get("modified_z_score", 0.0)))
                if 0.0 < anomaly_intensity < 10.0:
                    anomaly_intensity = min(100.0, anomaly_intensity * 10.0)
                break

    return calculate_meci(
        temp_amplitude_c=latest.get("temp_amplitude_c"),
        pressure_pa=p_latest,
        pressure_rate_of_change=dp_empirical,
        solar_longitude_ls=latest.get("solar_longitude_ls"),
        anomaly_intensity=anomaly_intensity,
        weights=weights
    )
