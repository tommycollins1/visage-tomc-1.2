"""
Oxford North Scenario Example Script for ViSAGE 1.1

This script:
- Loads origins and destinations
- Adds Oxford North as a new origin
- Recomputes the distance matrix
- Runs the scenario gravity model (baseline or quality)
- Computes site-level impacts
- Builds OD flows from Oxford North
- Produces the triptych visualisation
"""

import pandas as pd
import geopandas as gpd

# ------------------------------
# IMPORT MODULES
# ------------------------------

from paths_cfg import ARCHIVED_SYNTHETIC_ORIGINS, ARCHIVED_SITE_CATALOGUE_WITH_QUALITY
from params_cfg import (
    OXFORD_NORTH_ID,
    OXFORD_NORTH_EASTING,
    OXFORD_NORTH_NORTHING,
    OXFORD_NORTH_POPULATION,
)

from src.data.load_origins import load_origins
from src.data.load_destinations import load_destinations
from src.model.distance import build_distance_matrix

from src.behaviour.distance_decay import (
    LAMBDA_PANS,
    run_gravity_with_pans_lambda,
    run_gravity_with_lambda,
)

from src.model.quality_attractor import run_quality_sensitive_gravity

from src.scenario.add_origin import (
    add_new_origin,
    compute_extended_distance_matrix,
)

from src.scenario.run_scenario import (
    compute_scenario_visits,
    compute_impact,
)

from src.visualisation.scenario_tryptych import plot_triptych


# ------------------------------
# 1. PATHS
# ------------------------------
# NOTE: using the archived v1.1-format data here (see run_quality.py for why)

ORIGINS_PATH = ARCHIVED_SYNTHETIC_ORIGINS
DESTINATIONS_PATH = ARCHIVED_SITE_CATALOGUE_WITH_QUALITY


# ------------------------------
# 2. LOAD DATA
# ------------------------------

origins_gdf = load_origins(str(ORIGINS_PATH))
destinations_gdf = load_destinations(str(DESTINATIONS_PATH))


# ------------------------------
# 3. ADD OXFORD NORTH
# ------------------------------

origins_extended = add_new_origin(
    origins_gdf,
    origin_id=OXFORD_NORTH_ID,
    easting=OXFORD_NORTH_EASTING,
    northing=OXFORD_NORTH_NORTHING,
    population=OXFORD_NORTH_POPULATION,
)


# ------------------------------
# 4. RECOMPUTE DISTANCE MATRIX
# ------------------------------

dist_matrix_extended = compute_extended_distance_matrix(
    origins_extended,
    destinations_gdf,
)


# ------------------------------
# 5. RUN BASELINE (NO OXFORD NORTH)
# ------------------------------

baseline_df = run_gravity_with_pans_lambda(
    origins_gdf.drop(columns="geometry"),
    destinations_gdf.drop(columns="geometry"),
    build_distance_matrix(origins_gdf, destinations_gdf),
)

baseline_visits = (
    baseline_df.groupby("site_id")["visits"]
    .sum()
    .reset_index()
    .rename(columns={"visits": "visits_baseline"})
)


# ------------------------------
# 6. RUN SCENARIO (WITH OXFORD NORTH)
# ------------------------------

scenario_df, scenario_visits = compute_scenario_visits(
    origins_df=origins_extended.drop(columns="geometry"),
    destinations_df=destinations_gdf.drop(columns="geometry"),
    dist_matrix=dist_matrix_extended,
    # compute_scenario_visits always passes lambda_value as a keyword, so the
    # gravity function must accept it - run_gravity_with_pans_lambda doesn't
    # (it hard-codes LAMBDA_PANS internally). Use run_gravity_with_lambda
    # instead, passing LAMBDA_PANS explicitly: numerically identical result.
    gravity_function=run_gravity_with_lambda,
    lambda_value=LAMBDA_PANS,
)


# ------------------------------
# 7. COMPUTE IMPACT
# ------------------------------

impact_df = compute_impact(baseline_visits, scenario_visits)

print("\n=== TOP 20 IMPACTED SITES ===\n")
print(
    impact_df[
        ["site_id", "visits_baseline", "visits_scenario",
         "delta_visits", "pct_change"]
    ].head(20)
)


# ------------------------------
# 8. BUILD OD FLOWS FROM OXFORD NORTH
# ------------------------------

on_flows = scenario_df[scenario_df["origin_id"] == OXFORD_NORTH_ID].copy()
on_flows = on_flows.merge(
    destinations_gdf[["site_id", "geometry"]],
    on="site_id",
    how="left"
)

# Keep top 10 flows
on_flows = on_flows.nlargest(10, "visits")
flows_gdf = gpd.GeoDataFrame(on_flows, geometry="geometry", crs=destinations_gdf.crs)


# ------------------------------
# 9. PREPARE TRIPTYCH INPUT
# ------------------------------

trip = destinations_gdf.copy()

trip = trip.merge(baseline_visits, on="site_id", how="left")
trip = trip.merge(scenario_visits, on="site_id", how="left")

# Simple class bins (you can refine later)
trip["class_baseline"] = pd.qcut(trip["visits_baseline"], q=6, labels=False)
trip["class_scenario"] = pd.qcut(trip["visits_scenario"], q=6, labels=False)


# ------------------------------
# 10. PLOT TRIPTYCH
# ------------------------------

colour_map = {
    0: "#fee5d9",
    1: "#fcae91",
    2: "#fb6a4a",
    3: "#de2d26",
    4: "#a50f15",
    5: "#67000d",
}

plot_triptych(
    trip_df=trip,
    flows_gdf=flows_gdf,
    on_x=OXFORD_NORTH_EASTING,
    on_y=OXFORD_NORTH_NORTHING,
    colour_map=colour_map,
)
