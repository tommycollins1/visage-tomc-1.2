from paths_cfg import ARCHIVED_SYNTHETIC_ORIGINS, ARCHIVED_SITE_CATALOGUE_WITH_QUALITY
from params_cfg import BETA_QUALITY
from src.data.load_origins import load_origins
from src.data.load_destinations import load_destinations
from src.behaviour.distance_decay import LAMBDA_PANS
from src.model.quality_attractor import run_quality_sensitive_gravity
from src.model.distance import build_distance_matrix
from src.visualisation.ranking_comparisons import (
    build_ranking_comparison,
    plot_top_n_rank_change,
)


# ---------------------------------------------------------
# 1. PATHS
# ---------------------------------------------------------
# NOTE: using the archived v1.1-format data here, not the new
# site_cat_access_union.csv - the new file doesn't have QualityScore
# yet and isn't deduplicated to one row per site. Swap these once the new
# boolean-column destinations file + quality scores are ready.

ORIGINS_PATH = ARCHIVED_SYNTHETIC_ORIGINS
DESTINATIONS_PATH = ARCHIVED_SITE_CATALOGUE_WITH_QUALITY


# ---------------------------------------------------------
# 2. LOAD DATA
# ---------------------------------------------------------

origins_gdf = load_origins(str(ORIGINS_PATH))
destinations_gdf = load_destinations(str(DESTINATIONS_PATH))

# Ensure QualityScore exists
if "QualityScore" not in destinations_gdf.columns:
    raise ValueError("Expected 'QualityScore' column in site_catalogue_with_quality.csv")


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
