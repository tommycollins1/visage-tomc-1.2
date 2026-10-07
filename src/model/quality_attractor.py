"""
Quality Attractor Module for ViSAGE 1.1

This module implements:
- A placeholder OSM feature extraction skeleton (for future V1.2 integration)
- Loading of precomputed QualityScore values (from CSV)
- A quality-based attractiveness function A_j = QualityScore^beta
- A gravity model that incorporates both distance decay and quality
"""

import numpy as np
import pandas as pd

from src.behaviour.distance_decay import VISITS_PER_PERSON_PER_YEAR


# ---------------------------------------------------------
# 1. Placeholder OSM Feature Extractor (V1.2 Skeleton)
# ---------------------------------------------------------

def extract_osm_features_stub(destinations_gdf):
    """
    Placeholder for the OSM feature extraction pipeline.

    In ViSAGE 1.2 this will:
    - query OSM / Overture POI features
    - compute amenity counts, path density, naturalness, etc.
    - normalise and aggregate into a composite quality score

    For ViSAGE 1.1, this function simply returns the existing
    QualityScore column already present in the CSV.
    """
    if "QualityScore" not in destinations_gdf.columns:
        raise ValueError("Expected 'QualityScore' column in destinations_gdf")

    return destinations_gdf["QualityScore"].values


# ---------------------------------------------------------
# 2. Quality Attractor Function
# ---------------------------------------------------------

def quality_attractor(quality_scores, beta=1.0):
    """
    Compute attractiveness A_j from quality scores.

    A_j = (QualityScore)^beta

    Parameters
    ----------
    quality_scores : array-like
        Normalised quality scores in [0, 1]
    beta : float
        Behavioural sensitivity to quality

    Returns
    -------
    ndarray
        Attractiveness values A_j
    """
    return np.power(quality_scores, beta)


# ---------------------------------------------------------
# 3. Gravity Model with Quality
# ---------------------------------------------------------

def run_quality_sensitive_gravity(origins_df,
                                  destinations_df,
                                  dist_matrix,
                                  lambda_value,
                                  beta=1.0):
    """
    Gravity model incorporating quality-based attractiveness.

    Parameters
    ----------
    origins_df : DataFrame
        Must include 'origin_id' and 'population'
    destinations_df : DataFrame
        Must include 'site_id' and 'QualityScore'
    dist_matrix : DataFrame
        Distances in metres (origins x destinations)
    lambda_value : float
        Distance-decay parameter
    beta : float
        Quality sensitivity exponent

    Returns
    -------
    DataFrame (long-form):
        origin_id, site_id, visits
    """

    # 1. Extract quality scores (placeholder for future OSM pipeline)
    quality_scores = extract_osm_features_stub(destinations_df)

    # 2. Compute attractiveness A_j
    A_j = quality_attractor(quality_scores, beta=beta).reshape(1, -1)

    # 3. Distance-decay weights
    w = A_j * np.exp(-lambda_value * dist_matrix.values)

    # 4. Normalise per origin
    w_norm = w / w.sum(axis=1, keepdims=True)

    # 5. Visits per origin
    # NOTE (Sept 2026 fix): this previously used raw population with no
    # visits-per-person multiplier, putting visits_quality on a ~100x
    # different scale to visits_baseline (which does apply this multiplier
    # via run_gravity_with_pans_lambda / run_gravity_with_lambda). See
    # ISSUES.md #3b.
    origin_visits = (
        origins_df["population"].values.reshape(-1, 1) * VISITS_PER_PERSON_PER_YEAR
    )

    # 6. Allocate visits
    visits_matrix = origin_visits * w_norm

    # 7. Long-form output
    model_df = (
        pd.DataFrame(
            visits_matrix,
            index=origins_df["origin_id"],
            columns=destinations_df["site_id"],
        )
        .stack()
        .reset_index()
        .rename(columns={"level_0": "origin_id",
                         "level_1": "site_id",
                         0: "visits"})
    )

    return model_df
