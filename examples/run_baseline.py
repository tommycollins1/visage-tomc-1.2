"""
Baseline (distance-only) ViSAGE run, England scale.

All settings live in params_cfg.py (section "BASELINE RUN SETTINGS"); paths in
paths_cfg.py. Nothing is passed on the command line.

Writes the site-level result table (the canonical output):
    outputs/baseline_site_visits.csv   -> site_id, visits + run metadata
Optionally (params_cfg.SAVE_OD / PLOT):
    outputs/baseline_od_visits.parquet (origin x site visits)
    a map of the result (needs polygons whose polygon_id matches site_id)

Origins are processed in chunks: model_2 normalises per origin, so chunking
is exact, and it keeps memory bounded (the drive OSRM file is ~70M rows).

Optional sub-region runs: set params_cfg.CLIP_AREA (default None = full
England run). See src/data/clip_region.py for the reasoning. Clipped runs
write suffixed files (e.g. baseline_site_visits_oxford_demand.csv) so they
never overwrite the national result.
"""
from __future__ import annotations

import pandas as pd

import params_cfg as P
from paths_cfg import (
    SYNTHETIC_ORIGINS,
    GREENSPACE_DESTINATIONS,
    GREENSPACE_POLYGONS,
    DISTANCES_FINAL_BY_MODE,
    CLIP_BOUNDARIES,
    OUTPUTS,
    BASELINE_SITE_VISITS,
    BASELINE_OD_VISITS,
)
from src.data.load_origins import load_origins
from src.data.load_destinations import load_destinations
from src.model.spatial_interaction import model_2


def main():
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    method = P.DISTANCE_METHOD
    net_path = DISTANCES_FINAL_BY_MODE[P.NETWORK_MODE] if method == "network" else None
    max_snap = P.MAX_ORIGIN_SNAP_M if method == "network" else None

    origins_gdf = load_origins(path=SYNTHETIC_ORIGINS,
                               country_prefix=P.COUNTRY_PREFIX)
    dest_gdf = load_destinations(path=GREENSPACE_DESTINATIONS)

    # ---- optional clipping -------------------------------------------------
    region = None
    report_sites = None
    site_out, od_out = BASELINE_SITE_VISITS, BASELINE_OD_VISITS
    if P.CLIP_AREA:
        from src.data.clip_region import (
            load_region, select_origins, select_destinations, sites_in_region,
        )
        if P.CLIP_AREA not in CLIP_BOUNDARIES:
            raise KeyError(f"CLIP_AREA {P.CLIP_AREA!r} not in "
                           f"paths_cfg.CLIP_BOUNDARIES {list(CLIP_BOUNDARIES)}")
        region = load_region(
            CLIP_BOUNDARIES[P.CLIP_AREA], view=P.CLIP_VIEW,
            buffer_m=P.CLIP_BUFFER_M, clip_destinations=P.CLIP_DESTINATIONS,
            dest_buffer_m=P.DEST_BUFFER_M,
        )
        origins_gdf = select_origins(origins_gdf, region)
        dest_gdf = select_destinations(dest_gdf, region)
        if region.view == "supply":
            report_sites = sites_in_region(dest_gdf, region)
        suffix = (f"_{P.CLIP_AREA}_{region.view}"
                  + ("_closed" if P.CLIP_DESTINATIONS else ""))
        site_out = BASELINE_SITE_VISITS.with_name(
            f"{BASELINE_SITE_VISITS.stem}{suffix}{BASELINE_SITE_VISITS.suffix}")
        od_out = BASELINE_OD_VISITS.with_name(
            f"{BASELINE_OD_VISITS.stem}{suffix}{BASELINE_OD_VISITS.suffix}")

    origins = origins_gdf.drop(columns="geometry")
    destinations = dest_gdf.drop(columns="geometry")

    expected_total = float(origins["population"].sum() * P.VISITS_PER_PERSON_PER_YEAR)

    site_totals = pd.Series(dtype="float64")
    allocated_origins: set = set()
    od_writer = None

    for start in range(0, len(origins), P.CHUNK_SIZE):
        chunk = origins.iloc[start:start + P.CHUNK_SIZE]
        m2 = model_2(
            origins_df=chunk,
            destinations_df=destinations,
            visits_per_person=P.VISITS_PER_PERSON_PER_YEAR,
            lambda_value=P.LAMBDA_PANS,
            distance_method=method,
            network_distances_path=net_path,
            max_origin_snap_m=max_snap,
        )

        site_totals = site_totals.add(m2.groupby("site_id")["visits"].sum(),
                                      fill_value=0.0)
        allocated_origins.update(m2["origin_id"].unique())

        if P.SAVE_OD:
            import pyarrow as pa
            import pyarrow.parquet as pq
            tbl = pa.Table.from_pandas(m2, preserve_index=False)
            if od_writer is None:
                od_writer = pq.ParquetWriter(od_out, tbl.schema)
            od_writer.write_table(tbl)

        print(f"  origins {start:,}-{start + len(chunk):,} / {len(origins):,}",
              flush=True)

    if od_writer is not None:
        od_writer.close()

    # ---- site-level table (canonical output) ------------------------------
    site_visits = site_totals.rename("visits").rename_axis("site_id").reset_index()
    allocated = float(site_visits["visits"].sum())   # before any supply-view filter

    if report_sites is not None:   # supply view: report only sites in the area
        site_visits = site_visits[site_visits["site_id"].isin(report_sites)]

    site_visits["distance_method"] = method
    site_visits["network_mode"] = P.NETWORK_MODE if method == "network" else ""
    site_visits["lambda_value"] = P.LAMBDA_PANS
    site_visits["visits_per_person"] = P.VISITS_PER_PERSON_PER_YEAR
    if region is not None:
        site_visits["clip_area"] = region.name
        site_visits["clip_view"] = region.view
        site_visits["clip_buffer_m"] = region.buffer_m
        site_visits["clip_destinations"] = P.CLIP_DESTINATIONS
    site_visits.to_csv(site_out, index=False)

    # ---- sanity checks -----------------------------------------------------
    n_missing = len(set(origins["origin_id"]) - allocated_origins)
    print(f"\nWrote {site_out} ({len(site_visits):,} sites)")
    if P.SAVE_OD:
        print(f"Wrote {od_out}")
    print(f"Visits allocated: {allocated:,.0f} of {expected_total:,.0f} "
          f"({allocated / expected_total:.2%}); "
          f"{n_missing:,} origins received no allocation "
          f"(no sites within threshold, or dropped by snap filter)")
    print(site_visits["visits"].describe().round(0).to_string())

    if P.PLOT:
        import geopandas as gpd
        from src.visualisation.baseline_maps import plot_greenspace_visits_osm

        polygons = (gpd.read_file(GREENSPACE_POLYGONS)
                    .rename(columns={"polygon_id": "site_id"}))
        plot_greenspace_visits_osm(
            model_df=site_visits[["site_id", "visits"]],
            polygons_gdf=polygons,
            title="England Greenspace Visit Volume (Baseline, distance-only)",
            id_col="site_id",
        )


if __name__ == "__main__":
    main()
