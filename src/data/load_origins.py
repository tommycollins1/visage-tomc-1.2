

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


def load_origins(path) -> gpd.GeoDataFrame:
    """
    Load and prepare origin data (synthetic population).

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with origin_id, population, and geometry in EPSG:27700.
    """
    origins = pd.read_csv(path)

    # Deduplicate origins (keep latest entry per LSOA)
    origins = origins.drop_duplicates(subset="origin_id", keep="last")

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

