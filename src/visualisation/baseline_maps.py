import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

from paths_cfg import TILE_CACHE

# Cache fetched basemap tiles locally so repeated runs during development
# don't keep re-requesting the same tiles - this, combined with the much
# wider (~40km) extent since the edge-effect buffer work, was tripping
# rate-limiting/blocking on both OpenStreetMap's and CartoDB's tile servers.
TILE_CACHE.mkdir(parents=True, exist_ok=True)
ctx.set_cache_dir(str(TILE_CACHE))


def plot_greenspace_visits_osm(
    model_df: pd.DataFrame,
    polygons_gdf: gpd.GeoDataFrame,
    title: str = "Oxford Greenspace Visit Volume",
    id_col: str = "site_id",
):
    """
    Plot baseline greenspace visit volumes over an OSM basemap.

    Site polygons are drawn as a neutral context layer (no visits encoding -
    colouring the polygon itself by visits would conflate a site's physical
    size with how much it's actually visited). The visits signal (colour +
    size) is drawn as a proportional symbol at each polygon's TRUE centroid.

    This replaces the old approach of plotting one arbitrary access point
    per site (destinations_gdf.drop_duplicates(subset=id_col, keep="first"))
    - that picked whichever access point happened to be first in the file,
    which is why sites could previously plot off to one edge instead of
    their actual centre. destinations_gdf/access points are no longer
    needed here now that real site geometry is available.
    """

    # 1. Aggregate visits to site level
    site_visits = (
        model_df.groupby(id_col)["visits"]
        .sum()
        .reset_index()
    )

    # 2. Join onto polygon geometry - LEFT join, not inner, so a mismatched
    #    id doesn't silently vanish from the map. Report anything that
    #    doesn't match: the polygon file's id column may not line up
    #    cleanly with the model's site_ids.
    polygons_gdf = polygons_gdf.copy()
    polygons_gdf[id_col] = polygons_gdf[id_col].astype(str)
    site_visits[id_col] = site_visits[id_col].astype(str)

    gdf = polygons_gdf.merge(site_visits, on=id_col, how="left")
    n_matched = gdf["visits"].notna().sum()
    n_total = len(site_visits)
    if n_matched < n_total:
        missing = sorted(set(site_visits[id_col]) - set(polygons_gdf[id_col]))
        print(
            f"WARNING: only {n_matched}/{n_total} modelled sites matched a "
            f"polygon ({len(missing)} unmatched) - e.g. {missing[:5]}"
        )
    gdf = gdf[gdf["visits"].notna()].copy()

    # 3. Reproject to Web Mercator for the basemap
    gdf = gdf.to_crs(epsg=3857)

    # 4. Proportional-symbol points at each polygon's TRUE centroid
    gdf_points = gdf.copy()
    gdf_points["geometry"] = gdf_points.geometry.centroid

    # 5. Strong symbol scaling + minimum size
    gdf_points["size"] = np.maximum(np.sqrt(gdf_points["visits"]) / 4, 25)

    # 6. Six stepped colour bins using Plasma
    bins = pd.qcut(
        gdf_points["visits"],
        q=6,
        labels=["Very Low", "Low", "Medium", "High", "Very High", "Extreme"],
    )
    gdf_points["visit_bin"] = bins

    plasma = plt.cm.plasma
    colours = {
        "Very Low": plasma(0.05),
        "Low": plasma(0.20),
        "Medium": plasma(0.40),
        "High": plasma(0.60),
        "Very High": plasma(0.80),
        "Extreme": plasma(0.95),
    }

    # Compute rounded thresholds for legend labels
    qvals = gdf_points["visits"].quantile([0, 0.2, 0.4, 0.6, 0.8, 1]).tolist()
    q_round = [int(round(v, -3)) for v in qvals]

    approx_labels = [
        f"Very Low < {q_round[1]//1000}k",
        f"Low ~ {((q_round[1]+q_round[2])//2)//1000}k",
        f"Medium ~ {((q_round[2]+q_round[3])//2)//1000}k",
        f"High ~ {((q_round[3]+q_round[4])//2)//1000}k",
        f"Very High ~ {((q_round[4]+q_round[5])//2)//1000}k",
        f"Extreme > {q_round[5]//1000}k",
    ]

    # 7. Top 5 greenspaces
    top5 = gdf_points.nlargest(5, "visits")

    # 8. Plot
    fig, ax = plt.subplots(figsize=(12, 12))

    # Bounds - from the polygon layer, now the complete, correctly
    # geo-referenced dataset (previously referenced an undefined `gdf`
    # left over from before this function took a separate polygons input)
    xmin, ymin, xmax, ymax = gdf.total_bounds
    pad_x = (xmax - xmin) * 0.05
    pad_y = (ymax - ymin) * 0.05
    ax.set_xlim(xmin - pad_x, xmax + pad_x)
    ax.set_ylim(ymin - pad_y, ymax + pad_y)

    # Basemap
    # Esri's World Gray Canvas: free, no API key/account required, and a
    # light neutral style close to CartoDB Positron's look (which now
    # requires a registered API key for programmatic use - see CHANGELOG).
    # zoom is set explicitly rather than left to auto-calculate: the extent
    # is now ~40km across several towns, and auto-zoom was requesting far
    # more tiles than needed for a readable map at this scale, which is
    # part of what triggered rate-limiting.
    ctx.add_basemap(
        ax,
        source=ctx.providers.Esri.WorldGrayCanvas,
        zoom=11,
        alpha=0.8,
    )

    # Polygons (if present)
    if gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"]).any():
        gdf.plot(
            ax=ax,
            facecolor="none",
            edgecolor="black",
            linewidth=0.6,
            alpha=0.5,
        )

    # Proportional symbols
    for label, colour in colours.items():
        subset = gdf_points[gdf_points["visit_bin"] == label]
        subset.plot(
            ax=ax,
            markersize=subset["size"],
            color=colour,
            alpha=0.85,
            edgecolor="white",
            linewidth=0.4,
        )

    # Label top 5
    offsets = [(20, 20), (-20, 20), (20, -20), (-20, -20), (28, 0)]
    for (idx, row), (dx, dy) in zip(top5.iterrows(), offsets):
        ax.annotate(
            str(row[id_col]),
            xy=(row.geometry.x, row.geometry.y),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=10,
            fontweight="bold",
            color="black",
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"),
        )

    # Legend
    handles = []
    for i, (label, colour) in enumerate(colours.items()):
        handles.append(
            plt.Line2D(
                [0],
                [0],
                marker="o",
                markersize=np.sqrt(80 + i * 40),
                color=colour,
                linestyle="",
                markeredgecolor="white",
            )
        )

    ax.legend(
        handles,
        approx_labels,
        title="Visit Volume",
        loc="upper right",
        frameon=True,
        fontsize=9,
        title_fontsize=11,
    )

    # North arrow
    ax.annotate(
        "N",
        xy=(0.08, 0.12),
        xytext=(0.08, 0.02),
        arrowprops=dict(facecolor="black", width=4, headwidth=12),
        ha="center",
        va="center",
        fontsize=16,
        xycoords="axes fraction",
    )

    ax.set_title(title, fontsize=16)
    ax.set_axis_off()
    plt.subplots_adjust(left=0.02, right=0.98, top=0.97, bottom=0.02)
    plt.show()
