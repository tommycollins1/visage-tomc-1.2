"""
-------------------------------------------------------------------------------
Title: "params_cfg"
Description: "Single source of truth for model parameters used across
    ViSAGE 1.2 examples (visits per person, distance-decay lambda, quality
    sensitivity beta, Oxford North scenario definition). Paths live in
    paths_cfg.py - this file is model behaviour/tuning only.

    Distance-decay convention used throughout the codebase:
        weight = exp(-lambda_value * distance)
    lambda_value is a per-metre rate, NOT a metre length-scale. See
    CHANGELOG.md for the v1.1.1 fix that made this consistent across
    src/model/spatial_interaction.py, src/behaviour/distance_decay.py and
    src/model/quality_attractor.py.
"
Created: 12/08/2026
Author: tommycollins1 (trc207)
Notes:
    input:
    output:
-------------------------------------------------------------------------------
"""
from __future__ import annotations

from typing import Final

# =============================================================================
# BASELINE MODEL (model_2 / distance-only)
# =============================================================================
# Distance-decay lambda and visit frequency are calibrated from the PaNS
# survey (see src/behaviour/distance_decay.py for the regression fit) and
# re-exported here so every example script can pull all tuning parameters
# from this one file, per the module docstring above. Do not redefine a
# separate placeholder lambda/visits-per-person here - the Sept 2026 baseline
# lambda bug (1500m placeholder vs PaNS-calibrated ~7740m) came from exactly
# that: two names for the same concept living in two files.

from src.behaviour.distance_decay import (  # noqa: F401
    LAMBDA_PANS,
    VISITS_PER_PERSON_PER_YEAR,
)

# =============================================================================
# BASELINE RUN SETTINGS (read by examples/run_baseline.py)
# =============================================================================
# Edit these here - run_baseline.py takes no command-line arguments.

# Distance between origins and sites: "network" (OSRM road distance) or
# "euclidean" (straight line). NETWORK_MODE picks the OSRM extract
# ("drive" covers LAMBDA_PANS's range; "walk" caps at ~2.16km - see paths_cfg).
DISTANCE_METHOD: Final[str] = "network"
NETWORK_MODE: Final[str] = "drive"

# Keep origins whose id starts with this ("E" = England only; the origins file
# also holds Welsh "W01..." LSOAs that fall outside the England-only network).
# None keeps all origins.
COUNTRY_PREFIX: Final[str | None] = "E"

# Network only: drop origins OSRM had to snap further than this (metres) onto
# the road network. English origins are essentially all < 550m. None disables.
MAX_ORIGIN_SNAP_M: Final[float | None] = 1000

# Origins per model_2 call (exact - origins are normalised independently).
CHUNK_SIZE: Final[int] = 2000

# Outputs: the site table is always written; these are extras.
SAVE_OD: Final[bool] = False   # origin x site visits as parquet (large)
PLOT: Final[bool] = True      # map; needs polygons whose polygon_id matches site_id

# ---- Optional study-area clipping (None = full England run) -----------------
# Key into paths_cfg.CLIP_BOUNDARIES, e.g. "oxford". See src/data/clip_region.py
# for why origins are clipped but destinations are (by default) not.
CLIP_AREA: Final[str | None] = 'oxford'
# "demand": residents of the area -> anywhere (exact subset of the national run)
# "supply": visits to sites in the area, from origins in area + buffer
CLIP_VIEW: Final[str] = "demand"
# Buffer added to the area when selecting origins. None -> 0 (demand) / 28000 (supply)
CLIP_BUFFER_M: Final[float | None] = None
# Closed-system variant: ALSO restrict destinations (approximate; inflates rim sites)
CLIP_DESTINATIONS: Final[bool] = False
DEST_BUFFER_M: Final[float] = 16093   # with CLIP_DESTINATIONS: 10 miles

# =============================================================================
# QUALITY-SENSITIVE MODEL
# =============================================================================

BETA_QUALITY: Final[float] = 1.0  # quality sensitivity exponent, A_j = QualityScore ** beta

# =============================================================================
# OXFORD NORTH SCENARIO
# =============================================================================

OXFORD_NORTH_ID: Final[str] = "OXFORD_NORTH"
OXFORD_NORTH_EASTING: Final[float] = 451900
OXFORD_NORTH_NORTHING: Final[float] = 208000
OXFORD_NORTH_POPULATION: Final[float] = 4000
