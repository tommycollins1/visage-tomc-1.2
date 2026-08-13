"""
-------------------------------------------------------------------------------
Title: "paths_cfg"
Description: "Single source of truth for every filesystem path used across
    ViSAGE 1.2 (data inputs, archive, external/reference data, boundaries,
    outputs). Renamed from main_cfg.py - this file is paths only; model
    parameters (visits per person, lambda, beta, etc.) live in params_cfg.py."
Created: 11/08/2026
Author: tommycollins1 (trc207)
Notes:
    input:
    output:
-------------------------------------------------------------------------------
"""
from __future__ import annotations

from pathlib import Path
from typing import Final

# =============================================================================
# ROOTS + COMMON DIRECTORIES (searchable path segments)
# =============================================================================

ROOT: Final[Path] = Path(__file__).resolve().parent

DATA: Final[Path] = ROOT / "data"
REPORTS: Final[Path] = ROOT / "reports"
NOTEBOOKS: Final[Path] = ROOT / "notebooks"

# Data subfolders. See data/_archive - superseded v1.1-era files kept for
# reference (not deleted, just not part of the active pipeline).
DATA_ARCHIVE: Final[Path] = DATA / "_archive"
DATA_EXTERNAL: Final[Path] = DATA / "external"
DATA_BOUNDARIES: Final[Path] = DATA / "boundaries"

# =============================================================================
# ACTIVE MODEL INPUTS (current, in-use dataset)
# =============================================================================

SYNTHETIC_ORIGINS: Final[Path] = DATA / "ox_synthetic_pop_origin.csv"

# Access-point-level union of AGI/SSSI/SAC greenspace sites: one row per
# access point (2,926), has_agi/has_sac/has_sssi boolean columns for
# designation overlap (fixed 2026-08-12 - previously a site with multiple
# designations appeared as separate duplicate rows). Still multiple rows
# per site_id (458 sites) by design - see CHANGELOG for the plan to
# reduce this to one distance-per-site via nearest-access-point selection
# at distance-matrix build time, not by deleting rows here.
GREENSPACE_DESTINATIONS: Final[Path] = DATA / "site_cat_access_union.csv"

# =============================================================================
# ARCHIVED (superseded v1.1-format) INPUTS
# -----------------------------------------------------------------------------
# One row per site, includes QualityScore. Still needed for run_quality.py /
# run_oxford_north.py / run_quality_v12.py until quality scores + a clean
# one-row-per-site geometry exist in the new schema. Swap these out once
# that's ready.
# =============================================================================

ARCHIVED_SYNTHETIC_ORIGINS: Final[Path] = DATA_ARCHIVE / "synthetic_pop(in).csv"
ARCHIVED_SITE_CATALOGUE: Final[Path] = DATA_ARCHIVE / "site_catalogue(in).csv"
ARCHIVED_SITE_CATALOGUE_WITH_QUALITY: Final[Path] = DATA_ARCHIVE / "site_catalogue_with_quality.csv"
ARCHIVED_SITE_CATALOGUE_POLYGONS: Final[Path] = DATA_ARCHIVE / "site_catalogue_polygons.csv"

# =============================================================================
# EXTERNAL / REFERENCE DATA (not model inputs, used for validation/joins)
# =============================================================================

ORVAL_JOIN: Final[Path] = DATA_EXTERNAL / "join_orval.gpkg"
OVERTURE_JOIN: Final[Path] = DATA_EXTERNAL / "join_with_oxford.gpkg"
STRAVA_TIMESERIES: Final[Path] = DATA_EXTERNAL / "agg_strava_oxford_greenspace_timeseries.parquet"

# =============================================================================
# BOUNDARIES
# =============================================================================

OXFORD_LAD_BUFFER_10MI: Final[Path] = DATA_BOUNDARIES / "oxford_lad_buffer_10mi.gpkg"
