from __future__ import annotations

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


def load_origins(path, country_prefix: str | None = None) -> gpd.GeoDataFrame:
    """
    Load and prepare origin data (synthetic population).

    Parameters
    ----------
    path : path-like
        Origins CSV (origin_id, easting, northing, population).
    country_prefix : str, optional
        If given, keep only origins whose origin_id starts with this prefix.
        Use "E" for England-only runs: the all-origins file also contains
        Welsh LSOAs ("W01..."), which lie outside the England-only OSRM
        network and snap up to ~20km onto it, piling their demand onto a
        few border sites (Oct 2026 finding). None (default) keeps everything,
        so Oxford/archived-origin callers are unaffected.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with origin_id, population, and geometry in EPSG:27700.
    """
    origins = pd.read_csv(path)

    # Deduplicate origins (keep latest entry per LSOA)
    origins = origins.drop_duplicates(subset="origin_id", keep="last")

    if country_prefix is not None:
        n_before = len(origins)
        origins = origins[origins["origin_id"].astype(str).str.startswith(country_prefix)]
        print(f"load_origins: kept {len(origins):,}/{n_before:,} origins "
              f"with prefix {country_prefix!r}")

    # Rename coordinate columns for clarity
    origins = origins.rename(columns={"northing": "N", "easting": "E"})

    # Ensure numeric types
    origins["N"] = pd.to_numeric(origins["N"])
    origins["E"] = pd.to_numeric(origins["E"])
    origins["population"] = pd.to_numeric(origins["population"])

    # Build geometry
    gdf = gpd.GeoDataFrame(
        origins,
        geometry=gpd.points_from_xy(origins["E"], origins["N"]),
        crs="EPSG:27700",
    )

    return gdf

