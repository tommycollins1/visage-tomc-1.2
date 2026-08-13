import pandas as pd
import geopandas as gpd


def load_destinations(path) -> gpd.GeoDataFrame:
    """
    Load and prepare destination data (greenspace catalogue).

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with site_id and geometry in EPSG:27700.
    """
    destinations = pd.read_csv(path)

    destinations = destinations.rename(columns={"northing": "N", "easting": "E"})
    destinations["N"] = pd.to_numeric(destinations["N"])
    destinations["E"] = pd.to_numeric(destinations["E"])

    gdf = gpd.GeoDataFrame(
        destinations,
        geometry=gpd.points_from_xy(destinations["E"], destinations["N"]),
        crs="EPSG:27700",
    )

    return gdf
