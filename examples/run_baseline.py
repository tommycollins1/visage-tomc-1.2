from paths_cfg import SYNTHETIC_ORIGINS, GREENSPACE_DESTINATIONS
from params_cfg import VISITS_PER_PERSON, BASELINE_LAMBDA_VALUE
from src.data.load_origins import load_origins
from src.data.load_destinations import load_destinations
from src.model.spatial_interaction import model_2
from src.visualisation.baseline_maps import plot_greenspace_visits_osm


def main():
    origins_gdf = load_origins(path=SYNTHETIC_ORIGINS)
    destinations_gdf = load_destinations(path=GREENSPACE_DESTINATIONS)

    destinations_gdf = destinations_gdf[destinations_gdf.dataset == 'sssi']

    m2 = model_2(
        origins_df=origins_gdf.drop(columns="geometry"),
        destinations_df=destinations_gdf.drop(columns="geometry"),
        visits_per_person=VISITS_PER_PERSON,
        lambda_value=BASELINE_LAMBDA_VALUE,
    )

    plot_greenspace_visits_osm(
        model_df=m2,
        destinations_gdf=destinations_gdf,
        title="Oxford Greenspace Visit Volume (Baseline, distance-only)",
        id_col="access_pt_id",
    )


if __name__ == "__main__":
    breakpoint()
    main()
