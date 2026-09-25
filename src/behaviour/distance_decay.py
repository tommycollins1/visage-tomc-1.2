"""
Distance–decay calibration and gravity model functions for ViSAGE 1.1.

This module implements:
- PaNS-derived exponential decay calibration
- Behaviourally fitted lambda (λ)
- Gravity model allocation using calibrated λ
- Sensitivity variants (λ × 5, λ × 10, λ × 20, λ × 30)
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


# ---------------------------------------------------------
# 1. Behavioural calibration from PaNS (M2AQ6)
# ---------------------------------------------------------

# PaNS distance–probability points (metres, probabilities)
_PANS_DISTANCES_M = np.array([804, 2414, 10460, 19312]).reshape(-1, 1)
_PANS_PROBABILITIES = np.array([0.45, 0.23, 0.21, 0.11])

# Fit exponential decay: ln(P) = -λ d
_log_probs = np.log(_PANS_PROBABILITIES)
_model = LinearRegression(fit_intercept=False)
_model.fit(_PANS_DISTANCES_M, _log_probs)

# Behaviourally fitted lambda
LAMBDA_PANS = -_model.coef_[0]

# Behaviourally realistic visit frequency
VISITS_PER_PERSON_PER_YEAR = 100

# ---------------------------------------------------------
# 2. Gravity model using calibrated λ
# ---------------------------------------------------------


def run_gravity_with_pans_lambda(origins_df, sites_df, dist_matrix):
    """
    Gravity model using PaNS-calibrated lambda.

    Parameters
    ----------
    origins_df : DataFrame
        Must include 'origin_id' and 'population'.
    sites_df : DataFrame
        Must include 'site_id'.
    dist_matrix : DataFrame
        Index = origin_id, columns = site_id, values = distance (m).

    Returns
    -------
    DataFrame (long-form):
        origin_id, site_id, visits
    """

    # 1. Raw weights
    w = np.exp(-LAMBDA_PANS * dist_matrix.values)

    # 2. Normalise per origin
    w_norm = w / w.sum(axis=1, keepdims=True)

    # 3. Origin-level annual visits
    origin_visits = (
        origins_df["population"].values * VISITS_PER_PERSON_PER_YEAR
    ).reshape(-1, 1)

    # 4. Allocate visits
    visits_matrix = origin_visits * w_norm

    # 5. Long-form output
    model_df = (
        pd.DataFrame(
            visits_matrix,
            index=origins_df["origin_id"],
            columns=sites_df["site_id"],
        )
        .stack()
        .reset_index()
        .rename(columns={"level_0": "origin_id", "level_1": "site_id", 0: "visits"})
    )

    return model_df


# ---------------------------------------------------------
# 3. Generalised gravity model for λ-sensitivity
# ---------------------------------------------------------

def run_gravity_with_lambda(origins_df, sites_df, dist_matrix, lambda_value):
    """
    Gravity model using an arbitrary lambda (λ).

    Supports λ × 5, λ × 10, λ × 20, λ × 30 sensitivity analysis.
    """

    w = np.exp(-lambda_value * dist_matrix.values)
    w_norm = w / w.sum(axis=1, keepdims=True)

    origin_visits = (
        origins_df["population"].values * VISITS_PER_PERSON_PER_YEAR
    ).reshape(-1, 1)

    visits_matrix = origin_visits * w_norm

    model_df = (
        pd.DataFrame(
            visits_matrix,
            index=origins_df["origin_id"],
            columns=sites_df["site_id"],
        )
        .stack()
        .reset_index()
        .rename(columns={"level_0": "origin_id", "level_1": "site_id", 0: "visits"})
    )

    return model_df


# ---------------------------------------------------------
# 4. Predefined λ-multipliers for sensitivity analysis
# ---------------------------------------------------------

LAMBDA_5X = LAMBDA_PANS * 5
LAMBDA_10X = LAMBDA_PANS * 10
LAMBDA_20X = LAMBDA_PANS * 20
LAMBDA_30X = LAMBDA_PANS * 30
