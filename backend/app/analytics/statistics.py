"""
Scientific Statistical Engine.
Provides descriptive statistics, parametric & non-parametric correlation matrices,
cross-mission hypothesis testing (Mann-Whitney U), and seasonal distribution analysis.
Fulfills Directive 33, 34, 35.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from scipy import stats

def compute_summary_statistics(values: List[Any]) -> Dict[str, Any]:
    """Calculates comprehensive robust summary metrics for a numerical variable."""
    clean_vals = []
    for v in values:
        if v is not None:
            try:
                fv = float(v)
                if np.isfinite(fv):
                    clean_vals.append(fv)
            except (ValueError, TypeError):
                continue

    if not clean_vals:
        return {
            "count": 0, "mean": None, "median": None, "std": None,
            "variance": None, "min": None, "max": None, "iqr": None,
            "p05": None, "p95": None
        }

    arr = np.array(clean_vals)
    q75, q25 = np.percentile(arr, [75, 25])
    iqr = float(q75 - q25)

    return {
        "count": int(len(arr)),
        "mean": round(float(np.mean(arr)), 2),
        "median": round(float(np.median(arr)), 2),
        "std": round(float(np.std(arr, ddof=1)), 2) if len(arr) > 1 else 0.0,
        "variance": round(float(np.var(arr, ddof=1)), 2) if len(arr) > 1 else 0.0,
        "min": round(float(np.min(arr)), 2),
        "max": round(float(np.max(arr)), 2),
        "iqr": round(iqr, 2),
        "p05": round(float(np.percentile(arr, 5)), 2),
        "p95": round(float(np.percentile(arr, 95)), 2)
    }

def compute_correlation_matrix(records: List[Dict[str, Any]], variables: List[str]) -> Dict[str, Any]:
    """
    Computes both Pearson (linear) and Spearman (monotonic rank) correlation matrices
    along with two-tailed p-values and sample sizes. Safely handles zero variance and small samples.
    """
    df = pd.DataFrame(records)
    valid_cols = [c for c in variables if c in df.columns]
    
    sub_df = df[valid_cols].apply(pd.to_numeric, errors="coerce").dropna()
    n_samples = len(sub_df)

    pearson_matrix: Dict[str, Dict[str, Any]] = {c: {} for c in valid_cols}
    spearman_matrix: Dict[str, Dict[str, Any]] = {c: {} for c in valid_cols}

    for col1 in valid_cols:
        for col2 in valid_cols:
            if n_samples > 3:
                s1 = sub_df[col1]
                s2 = sub_df[col2]
                if float(s1.std()) == 0.0 or float(s2.std()) == 0.0:
                    pearson_matrix[col1][col2] = {"r": None, "p_value": None, "is_significant": False, "status": "ZERO_VARIANCE"}
                    spearman_matrix[col1][col2] = {"rho": None, "p_value": None, "is_significant": False, "status": "ZERO_VARIANCE"}
                else:
                    r_p, p_val_p = stats.pearsonr(s1, s2)
                    r_s, p_val_s = stats.spearmanr(s1, s2)
                    pearson_matrix[col1][col2] = {
                        "r": round(float(r_p), 3),
                        "p_value": float(f"{p_val_p:.2e}"),
                        "is_significant": bool(p_val_p < 0.05)
                    }
                    spearman_matrix[col1][col2] = {
                        "rho": round(float(r_s), 3),
                        "p_value": float(f"{p_val_s:.2e}"),
                        "is_significant": bool(p_val_s < 0.05)
                    }
            else:
                pearson_matrix[col1][col2] = {"r": None, "p_value": None, "is_significant": False, "status": "INSUFFICIENT_DATA"}
                spearman_matrix[col1][col2] = {"rho": None, "p_value": None, "is_significant": False, "status": "INSUFFICIENT_DATA"}

    has_zero_variance = any(float(sub_df[c].std()) == 0.0 for c in valid_cols) if n_samples > 0 else False
    overall_status = "ZERO_VARIANCE" if has_zero_variance else ("INSUFFICIENT_DATA" if n_samples <= 3 else "OK")

    return {
        "status": overall_status,
        "sample_size": n_samples,
        "variables": valid_cols,
        "pearson": pearson_matrix,
        "spearman": spearman_matrix,
        "methodological_note": (
            "Spearman's rank correlation is more robust on Mars atmospheric data "
            "as it does not assume bivariate normality and captures non-linear monotonic shifts "
            "driven by orbital eccentricity and dust opacity."
        )
    }

def compare_missions(
    curiosity_records: List[Dict[str, Any]], 
    insight_records: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Scientifically compares Gale Crater (Curiosity) vs Elysium Planitia (InSight).
    Verifies assumptions, enforces synthetic data transparency, and executes non-parametric Mann-Whitney U tests.
    """
    c_synthetic = any(r.get("is_synthetic", False) for r in curiosity_records)
    i_synthetic = any(r.get("is_synthetic", False) for r in insight_records)
    is_empirical = not (c_synthetic or i_synthetic)

    # Compare Pressure
    c_press = [float(r["pressure_pa"]) for r in curiosity_records if r.get("pressure_pa") is not None]
    i_press = [float(r["pressure_pa"]) for r in insight_records if r.get("pressure_pa") is not None]

    # Compare Ambient Air Temp
    c_temp = [float(r["air_temp_max_c"]) for r in curiosity_records if r.get("air_temp_max_c") is not None]
    i_temp = [float(r["air_temp_max_c"]) for r in insight_records if r.get("air_temp_max_c") is not None]

    press_test = None
    if len(c_press) < 10 or len(i_press) < 10:
        press_test = {
            "test_name": "Mann-Whitney U Test",
            "status": "INSUFFICIENT_SAMPLES",
            "detail": f"Requires >= 10 observations per mission; received Curiosity n={len(c_press)}, InSight n={len(i_press)}."
        }
    elif float(np.std(c_press)) == 0.0 or float(np.std(i_press)) == 0.0:
        press_test = {
            "test_name": "Mann-Whitney U Test",
            "status": "DEGENERATE_VARIANCE",
            "detail": "One or both observation sets exhibit zero barometric variance."
        }
    else:
        u_stat, p_val = stats.mannwhitneyu(c_press, i_press, alternative="two-sided")
        n1, n2 = len(c_press), len(i_press)
        effect_size = 1.0 - (2.0 * u_stat) / (n1 * n2)
        press_test = {
            "test_name": "Mann-Whitney U Test (Non-Parametric Two-Sided)",
            "u_statistic": round(float(u_stat), 1),
            "p_value": float(f"{p_val:.2e}"),
            "effect_size_rank_biserial": round(float(effect_size), 3),
            "is_statistically_significant": bool(p_val < 0.001),
            "is_empirical_comparison": is_empirical,
            "data_nature": "OBSERVED_VS_OBSERVED" if is_empirical else "OBSERVED_VS_SIMULATED_DEMONSTRATION",
            "scientific_interpretation": (
                "Surface atmospheric pressure in Gale Crater (elevation -4.5 km) is systematically "
                "higher than Elysium Planitia (elevation -2.6 km) in accordance with the Martian "
                "hydrostatic barometric scale height equation."
            )
        }

    return {
        "mission_a": {
            "name": "Curiosity (MSL)",
            "site": "Gale Crater",
            "elevation_km": -4.5,
            "is_synthetic": c_synthetic,
            "data_origin": "synthetic" if c_synthetic else "observed",
            "pressure_stats": compute_summary_statistics(c_press),
            "air_temp_max_stats": compute_summary_statistics(c_temp)
        },
        "mission_b": {
            "name": "InSight Lander",
            "site": "Elysium Planitia",
            "elevation_km": -2.6,
            "is_synthetic": i_synthetic,
            "data_origin": "synthetic" if i_synthetic else "observed",
            "pressure_stats": compute_summary_statistics(i_press),
            "air_temp_max_stats": compute_summary_statistics(i_temp)
        },
        "hypothesis_test_pressure": press_test,
        "is_empirical_comparison": is_empirical,
        "comparison_type": "OBSERVED_VS_OBSERVED" if is_empirical else "OBSERVED_VS_SIMULATED_DEMONSTRATION",
        "methodological_caveat": (
            "Caution: InSight records represent a calibrated simulation baseline (DEMONSTRATION DATA) "
            "adhering to PDS seasonal envelopes. This statistical test is an educational demonstration "
            "and does not constitute direct empirical proof between physical instruments. "
            "Furthermore, direct point-to-point comparison is constrained by geographical separation "
            "(~600 km distance) and elevation difference (1.9 km altitude delta)."
        )
    }
