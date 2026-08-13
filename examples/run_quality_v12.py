from pathlib import Path

from paths_cfg import ARCHIVED_SYNTHETIC_ORIGINS, ARCHIVED_SITE_CATALOGUE_WITH_QUALITY, NOTEBOOKS
from params_cfg import BETA_QUALITY
from src.data.load_origins import load_origins
from src.data.load_destinations import load_destinations
from src.behaviour.distance_decay import LAMBDA_PANS
from src.model_v12.quality_attractor import run_quality_sensitive_gravity
from src.model.distance import build_distance_matrix
from src.visualisation.ranking_comparisons import (
    build_ranking_comparison,
    plot_top_n_rank_change,
)


# ---------------------------------------------------------
# 1. PATHS
# ---------------------------------------------------------
# NOTE: using the archived v1.1-format data here (see run_quality.py for why)

ORIGINS_PATH = ARCHIVED_SYNTHETIC_ORIGINS
DESTINATIONS_PATH = ARCHIVED_SITE_CATALOGUE_WITH_QUALITY


# ---------------------------------------------------------
# 2. LOAD DATA
# ---------------------------------------------------------

origins_gdf = load_origins(str(ORIGINS_PATH))
destinations_gdf = load_destinations(str(DESTINATIONS_PATH))

# Fix column name if using VISAGE 1.1 format
if "quality" not in destinations_gdf.columns:
    if "QualityScore" in destinations_gdf.columns:
        destinations_gdf = destinations_gdf.rename(columns={"QualityScore": "quality"})
    else:
        raise ValueError("Expected 'quality' or 'QualityScore' column in site_catalogue_with_quality.csv")




# ---------------------------------------------------------
# 3. BUILD DISTANCE MATRIX
# ---------------------------------------------------------

dist_matrix = build_distance_matrix(origins_gdf, destinations_gdf)


# ---------------------------------------------------------
# 4. RUN BASELINE (distance-only)
# ---------------------------------------------------------

from src.behaviour.distance_decay import run_gravity_with_pans_lambda

baseline_df = run_gravity_with_pans_lambda(
    origins_gdf.drop(columns="geometry"),
    destinations_gdf.drop(columns="geometry"),
    dist_matrix
)


# ---------------------------------------------------------
# 5. RUN QUALITY-SENSITIVE MODEL
# ---------------------------------------------------------

quality_df = run_quality_sensitive_gravity(
    origins_df=origins_gdf.drop(columns="geometry"),
    destinations_df=destinations_gdf.drop(columns="geometry"),
    dist_matrix=dist_matrix,
    lambda_value=LAMBDA_PANS,
    beta=BETA_QUALITY,
)


# ---------------------------------------------------------
# 6. BUILD RANKING COMPARISON TABLE
# ---------------------------------------------------------

ranking = build_ranking_comparison(baseline_df, quality_df)

print("\n=== TOP 20 RANKING COMPARISON ===\n")
print(
    ranking[
        ["site_id", "visits_baseline", "visits_quality",
         "rank_baseline", "rank_quality", "rank_change"]
    ].head(20)
)


# ---------------------------------------------------------
# 7. PLOT RANK CHANGE FOR TOP 10 QUALITY SITES
# ---------------------------------------------------------

plot_top_n_rank_change(ranking, top_n=10)

# ---------------------------------------------------------
# 8. AGGREGATE QUALITY MODEL TO SITE LEVEL
# ---------------------------------------------------------

site_visits = (
    quality_df.groupby("site_id", as_index=False)["visits"]
              .sum()
              .rename(columns={"visits": "predicted_visits"})
)

# ---------------------------------------------------------
# 9. SAVE FINAL SITE-LEVEL PREDICTIONS
# ---------------------------------------------------------

out_path = NOTEBOOKS / "visage_site_level_predictions.csv"
site_visits.to_csv(out_path, index=False)

print(f"\nSaved site-level predictions to: {out_path}\n")

