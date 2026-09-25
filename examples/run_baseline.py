import geopandas as gpd

from paths_cfg import (
    SYNTHETIC_ORIGINS,
    GREENSPACE_DESTINATIONS,
    GREENSPACE_POLYGONS_OX
)
from params_cfg import (
    VISITS_PER_PERSON_PER_YEAR,
    LAMBDA_PANS,
)
from src.data.load_origins import load_origins
from src.data.load_destinations import load_destinations
from src.model.spatial_interaction import model_2
from src.visualisation.baseline_maps import plot_greenspace_visits_osm


def main():
    origins_gdf = load_origins(path=SYNTHETIC_ORIGINS)
    destinations_gdf = load_destinations(path=GREENSPACE_DESTINATIONS)
    polygons = (gpd.read_file(GREENSPACE_POLYGONS_OX)
                .rename(columns={'polygon_id': "site_id"}))

    m2 = model_2(
        origins_df=origins_gdf.drop(columns="geometry"),
        destinations_df=destinations_gdf.drop(columns="geometry"),
        visits_per_person=VISITS_PER_PERSON_PER_YEAR,
        lambda_value=LAMBDA_PANS,
    )

    plot_greenspace_visits_osm(
        model_df=m2,
        polygons_gdf=polygons,
        title="Oxford Greenspace Visit Volume (Baseline, distance-only)",
        id_col="site_id",
    )


if __name__ == "__main__":
    main()
