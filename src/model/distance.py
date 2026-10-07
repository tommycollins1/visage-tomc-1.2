"""
Shared distance calculation for ViSAGE 1.2.

Single source of truth for "how far apart are two points" so that a future
Euclidean/network swap only has one place to change, instead of the four
separate copies that existed before this file (src/model/spatial_interaction.py,
src/model_v12/spatial_interaction.py, src/scenario/add_origin.py, and inline
in examples/run_quality.py and examples/run_quality_v12.py).

Network distance (OSRM) is wired in via `load_network_distances` below.
model_2 (src/model/spatial_interaction.py) takes a `distance_method` param
to switch between "euclidean" and "network" - see that module.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

import numpy as np
import pandas as pd
import pyarrow.dataset as pa_ds

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


def load_network_distances(
    distances_path,
    destinations_df: pd.DataFrame,
    origin_ids: Iterable[str] | None = None,
    dest_id_col: str = "dest_id",
    access_pt_col: str = "access_pt_id",
    site_id_col: str = "site_id",
) -> pd.DataFrame:
    """
    Load pre-computed OSRM network distances (walk or drive - see
    paths_cfg.DISTANCES_FINAL_WALK / DISTANCES_FINAL_DRIVE) and remap them
    to the CURRENT site_id scheme.

    IMPORTANT: the `site_id` column inside the OSRM parquet is from a
    different, stale vintage of the greenspace union (checked Sept 2026:
    near-zero overlap with the current site_cat_access_union.csv site_id
    values - a live symptom of the tile-artifact site-identity bug, see
    ISSUES.md #1/#7). It is dropped entirely here and re-derived by joining
    `dest_id` against `destinations_df`'s `access_pt_id` -> `site_id`
    mapping instead, which is the one actually in use right now.

    Parameters
    ----------
    distances_path : path-like
        Path to a distances_final.parquet file (one row per
        origin/access-point pair, columns include origin_id, dest_id,
        dist_m - see paths_cfg for walk vs drive).
    destinations_df : pd.DataFrame
        The CURRENT destinations catalogue (e.g. loaded from
        paths_cfg.GREENSPACE_DESTINATIONS). Must contain `access_pt_col`
        and `site_id_col`.
    origin_ids : iterable of str, optional
        Restrict the read to these origin_ids via predicate pushdown
        (Parquet filter, not a post-hoc pandas filter) - the drive file is
        ~70M rows / ~900MB, so this matters for memory, not just speed.

    Returns
    -------
    pd.DataFrame
        Long-form: origin_id, site_id, distance (metres). Access points
        with no match in destinations_df (i.e. not in the current
        catalogue) are dropped, not silently kept as orphans.
    """
    filt = None
    if origin_ids is not None:
        filt = pa_ds.field("origin_id").isin(list(origin_ids))

    dataset = pa_ds.dataset(str(distances_path), format="parquet")
    table = dataset.to_table(
        filter=filt,
        columns=["origin_id", "dest_id", "dist_m"],
    )
    df = table.to_pandas()

    lookup = destinations_df[[access_pt_col, site_id_col]].drop_duplicates()
    df = df.merge(lookup, left_on=dest_id_col, right_on=access_pt_col, how="inner")

    return df.rename(columns={"dist_m": "distance"})[
        ["origin_id", site_id_col, "distance"]
    ]
