import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx


def plot_greenspace_visits_osm(
    model_df: pd.DataFrame,
    destinations_gdf: gpd.GeoDataFrame,
    title: str = "Oxford Greenspace Visit Volume",
    id_col: str = "site_id",
):
    """
    Plot baseline greenspace visit volumes over an OSM basemap.
    """

    # 1. Aggregate visits
    site_visits = (
        model_df.groupby(id_col)["visits"]
        .sum()
        .reset_index()
    )

    # 2. Merge with geometries
    gdf = destinations_gdf.merge(site_visits, on=id_col, how="left")

    # 3. Reproject to Web Mercator
    gdf = gdf.to_crs(epsg=3857)

    # 4. Centroids for proportional symbols
    gdf_points = gdf.copy()
    # gdf_points["geometry"] = gdf_points.geometry.centroid

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
        f"Extreme > {q_round[4]//1000}k",
    ]

    # 7. Top 5 greenspaces
    top5 = gdf_points.nlargest(5, "visits")

    # 8. Plot
    fig, ax = plt.subplots(figsize=(12, 12))

    # Bounds
    xmin, ymin, xmax, ymax = gdf.total_bounds
    pad_x = (xmax - xmin) * 0.05
    pad_y = (ymax - ymin) * 0.05
    ax.set_xlim(xmin - pad_x, xmax + pad_x)
    ax.set_ylim(ymin - pad_y, ymax + pad_y)

    # Basemap
    ctx.add_basemap(
        ax,
        source=ctx.providers.CartoDB.Positron,
        zoom=13,
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
            # markersize=subset["size"],
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
