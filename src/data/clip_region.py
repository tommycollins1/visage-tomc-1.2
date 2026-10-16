"""
Optional study-area clipping for ViSAGE runs (England-scale model, sub-region
results). NOT used unless a run asks for it - the default pipeline is
unchanged.

Why origins are clipped but (by default) destinations are not
--------------------------------------------------------------
model_2 normalises each origin's visits across the sites it can reach, so an
origin's allocation depends only on ITS OWN choice set. Clipping ORIGINS
therefore gives results that are an exact subset of the England-wide run.
Clipping DESTINATIONS removes competitors, which inflates the remaining
sites' visits (most at the rim of the clipped area). Tested on Oxford
(Oct 2026), vs the England-wide run, for sites within 4.5km of the centre:

    origins in 10mi buffer, ALL destinations .... exact (within 1%)
    origins AND destinations in 10mi buffer ..... +1.6% mean, worst site 5%
                                                  (rim sites up to ~+20%)

Two views of the selected area
------------------------------
demand  People who LIVE in the area -> where they go (sites anywhere).
        Origins = those inside the area. Exact subset of the national run.
supply  Sites IN the area -> who visits them.
        Origins = those inside the area buffered by `buffer_m` (visitors come
        from outside it), all destinations kept, then the output is restricted
        to sites inside the (unbuffered) area. 28km ~ the drive extract's
        reach; ~16km (10mi) captured ~100% of visits to sites <=4.5km from
        the centre of Oxford, so sites nearer the rim need the larger buffer.

Optional `clip_destinations` gives the closed-system variant (origins and
destinations both restricted) - an approximation, kept for comparison with the
original Oxford design.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd

# 20-min drive cap in the OSRM extract reaches ~27.9km
DEFAULT_SUPPLY_BUFFER_M = 28_000
# 10 miles - the buffer used in the original Oxford design
DEFAULT_DEST_BUFFER_M = 16_093


@dataclass
class Region:
    name: str
    geometry: object          # shapely (multi)polygon, EPSG:27700
    view: str                 # "demand" | "supply"
    buffer_m: float
    origin_area: object       # geometry used to select origins
    dest_area: object | None  # geometry used to clip destinations (or None)


def load_region(boundary_path, view: str = "demand",
                buffer_m: float | None = None,
                clip_destinations: bool = False,
                dest_buffer_m: float = DEFAULT_DEST_BUFFER_M,
                name_col: str = "LAD24NM") -> Region:
    if view not in ("demand", "supply"):
        raise ValueError(f"view must be 'demand' or 'supply', got {view!r}")

    gdf = gpd.read_file(boundary_path)
    if gdf.crs is None or gdf.crs.to_epsg() != 27700:
        gdf = gdf.to_crs(27700)
    geom = gdf.geometry.union_all() if hasattr(gdf.geometry, "union_all") \
        else gdf.geometry.unary_union

    if buffer_m is None:
        buffer_m = DEFAULT_SUPPLY_BUFFER_M if view == "supply" else 0.0
    origin_area = geom.buffer(buffer_m) if buffer_m else geom
    dest_area = origin_area.buffer(dest_buffer_m) if clip_destinations else None

    name = (str(gdf[name_col].iloc[0]) if name_col in gdf.columns
            else Path(boundary_path).stem)
    return Region(name, geom, view, float(buffer_m), origin_area, dest_area)


def select_origins(origins_gdf: gpd.GeoDataFrame, region: Region) -> gpd.GeoDataFrame:
    out = origins_gdf[origins_gdf.within(region.origin_area)]
    print(f"clip[{region.view}] {region.name}: kept {len(out):,}/{len(origins_gdf):,} "
          f"origins (buffer {region.buffer_m:,.0f}m)")
    return out


def select_destinations(dest_gdf: gpd.GeoDataFrame, region: Region) -> gpd.GeoDataFrame:
    if region.dest_area is None:
        return dest_gdf
    out = dest_gdf[dest_gdf.within(region.dest_area)]
    print(f"clip: destinations restricted to {len(out):,}/{len(dest_gdf):,} "
          f"access points (closed-system variant; approximate)")
    return out


def sites_in_region(dest_gdf: gpd.GeoDataFrame, region: Region) -> set:
    """site_ids with at least one access point inside the (unbuffered) area."""
    return set(dest_gdf.loc[dest_gdf.within(region.geometry), "site_id"])
