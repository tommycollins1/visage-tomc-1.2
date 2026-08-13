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

VISITS_PER_PERSON: Final[float] = 50  # placeholder, annual visits per person

# model_2's old placeholder decay length-scale was 1500m (1.5km), expressed
# as exp(-distance / decay_length_m). Converted here to the codebase-standard
# rate convention: exp(-lambda_value * distance).
BASELINE_DECAY_LENGTH_M: Final[float] = 1500
BASELINE_LAMBDA_VALUE: Final[float] = 1 / BASELINE_DECAY_LENGTH_M

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
