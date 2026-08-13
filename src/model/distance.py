"""
Shared distance calculation for ViSAGE 1.2.

Single source of truth for "how far apart are two points" so that a future
Euclidean/network swap only has one place to change, instead of the four
separate copies that existed before this file (src/model/spatial_interaction.py,
src/model_v12/spatial_interaction.py, src/scenario/add_origin.py, and inline
in examples/run_quality.py and examples/run_quality_v12.py).

Everything here is Euclidean today. When network distance is wired in
(OSRM), add a `method="euclidean" | "network"` parameter to
build_distance_matrix rather than duplicating it again.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    import geopandas as gpd


def bng_distance(E1, N1, E2, N2):
    """Euclidean distance in British National Grid (metres)."""
    return np.sqrt((E1 - E2) ** 2 + (N1 - N2) ** 2)


def build_distance_matrix(
    origins_gdf: "gpd.GeoDataFrame",
    destinations_gdf: "gpd.GeoDataFrame",
    origin_id_col: str = "origin_id",
    dest_id_col: str = "site_id",
) -> pd.DataFrame:
    """
    Build a full origin x destination Euclidean distance matrix from two
    GeoDataFrames (point geometries, same CRS).

    Parameters
    ----------
    origins_gdf : gpd.GeoDataFrame
        Must contain `origin_id_col` and a point geometry column.
    destinations_gdf : gpd.GeoDataFrame
        Must contain `dest_id_col` and a point geometry column.
    origin_id_col, dest_id_col : str
        Column names to index the resulting matrix by.

    Returns
    -------
    pd.DataFrame
        Distance matrix in metres, index = origin ids, columns = destination ids.
    """
    orig_xy = np.vstack([origins_gdf.geometry.x, origins_gdf.geometry.y]).T
    dest_xy = np.vstack([destinations_gdf.geometry.x, destinations_gdf.geometry.y]).T

    return pd.DataFrame(
        np.sqrt(((orig_xy[:, None, :] - dest_xy[None, :, :]) ** 2).sum(axis=2)),
        index=origins_gdf[origin_id_col],
        columns=destinations_gdf[dest_id_col],
    )
