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
