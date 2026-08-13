"""
Scenario Engine: Adding new origins (e.g., Oxford North) to ViSAGE.

This module:
- Adds a new origin with coordinates + population
- Appends it to the existing origins GeoDataFrame
- Recomputes the origin × destination distance matrix
"""

import pandas as pd
import geopandas as gpd

from src.model.distance import build_distance_matrix


def add_new_origin(origins_gdf, origin_id, easting, northing, population):
    """
    Add a new origin (e.g., Oxford North) to the origins GeoDataFrame.
    """

    new_origin = pd.DataFrame({
        "origin_id": [origin_id],
        "easting": [easting],
        "northing": [northing],
        "population": [population],
    })

    new_origin_gdf = gpd.GeoDataFrame(
        new_origin,
        geometry=gpd.points_from_xy(new_origin.easting, new_origin.northing),
        crs=origins_gdf.crs,
    )

    return pd.concat([origins_gdf, new_origin_gdf], ignore_index=True)


def compute_extended_distance_matrix(origins_gdf, destinations_gdf):
    """
    Compute full origin × destination Euclidean distance matrix.
    """
    return build_distance_matrix(origins_gdf, destinations_gdf)
