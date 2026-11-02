"""Self-explanatory story maps, 1080 by 1920, from the same analysis outputs as the manual."""
import json

import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from research_helpers import carto
from sarlib import DATA, FIG, read, stretch

carto.use_style()
AUTHOR = "Ahmad Ammar | ahmadammar.github.io"

# Sindh
a, _, _, b, _ = read(DATA / "sindh_flood_100m.tif")
before, after, occ = a
st = json.loads((DATA / "sindh_stats.json").read_text())
thr = st["threshold"]
flood = (after < thr) & ~(before < thr) & (occ < 50)
usual = (after < thr) & (occ >= 50)
cls = np.where(usual, 1, np.where(flood, 2, np.nan))
utm = ccrs.UTM(42)
ext = (b.left, b.right, b.bottom, b.top)


def sindh(ax, fig):
    ax.imshow(stretch(after, 2, 98), cmap="gray", extent=ext, origin="upper", transform=utm)
    ax.imshow(np.ma.masked_invalid(cls), cmap=ListedColormap(["#0072B2", "#E69F00"]), vmin=1, vmax=2, extent=ext, origin="upper", transform=utm, interpolation="nearest")
    ax.set_extent(ext, utm)
    ax.gridlines(linewidth=0.2, color="white", alpha=0.4)
    carto.mark(ax, [(1, 67.68, 26.42), (2, 67.78, 26.73), (3, 67.86, 26.42), (4, 68.37, 26.25)], size=6.5)
    carto.scale_bar(ax, "lower right")
    rivers = gpd.read_file(DATA / "indus_river_lines.geojson")
    ax.add_geometries(rivers.geometry, ccrs.PlateCarree(), facecolor="none", edgecolor="white", linewidth=1.8, zorder=8)
    ax.add_geometries(rivers.geometry, ccrs.PlateCarree(), facecolor="none", edgecolor="#00E5FF", linewidth=0.9, zorder=9)
    pos = ax.get_position()
    carto.locator(fig, [pos.x0 + 0.015, pos.y0 + 0.012, 0.2, 0.105], [60, 78, 23, 38], (67.3, 68.6, 26.0, 27.4))


carto.story_map(FIG / "story_sindh_flood_2022", utm, sindh,
    title="Sindh under water, 2022", subtitle=f"Radar shows about {st['floodKm']:,} km\u00b2 of flood here, September 2022. Unvalidated.",
    legend=[("#E69F00", "Flood"), ("#0072B2", "Usual water"), ("#00E5FF", "Indus, generalised"), ("#111111", "Dark both years")],
    key=[(1, "Manchar Lake", "new water spreads along the hills"), (2, "Dadu", "higher ground amid the flood"), (3, "Sehwan", "hills pinch the valley"), (4, "Nawabshah", "may include wet fields")],
    method=f"Sentinel-1 VV, Aug-Sep 2021 and 2022, 100 m. Water is below {thr} dB (Otsu); flood is wet only in 2022, and water under 50% of the time in JRC.",
    source="Copernicus Sentinel; JRC; HydroRIVERS.", author=AUTHOR, map_share=0.69)

# London
a, _, _, b, _ = read(DATA / "london_2024_mean_40m.tif")
rgb = np.dstack([stretch(a[0]), stretch(a[1]), stretch(a[2])])
osgb = ccrs.OSGB()
ext2 = (b.left, b.right, b.bottom, b.top)
n = json.loads((DATA / "london_stats.json").read_text())["nScenesLondon"]


def london(ax, fig):
    ax.imshow(rgb, extent=ext2, origin="upper", transform=osgb, interpolation="nearest")
    ax.set_extent(ext2, osgb)
    ax.gridlines(linewidth=0.2, color="white", alpha=0.4)
    carto.mark(ax, [(1, -0.46, 51.47), (2, -0.118, 51.508), (3, -0.165, 51.507), (4, -0.02, 51.505), (5, -0.275, 51.445), (6, -0.495, 51.44)], size=6.5)
    carto.scale_bar(ax, "lower right")


carto.story_map(FIG / "story_london_radar", osgb, london,
    title="London, seen by radar", subtitle="A year of satellite radar shown in colour. Dark is smooth; bright is rough or built.",
    legend=[("#E8F050", "Dense city"), ("#D070E8", "Built-up"), ("#5F9F2F", "Plants"), ("#000080", "Water")],
    key=[(1, "Heathrow", "smooth runways"), (2, "Thames", "calm water looks dark"), (3, "Hyde Park", "grass, a dark gap"), (4, "Canary Wharf", "towers, strongest return"), (5, "Richmond Park", "open grassland"), (6, "Reservoir", "very still water")],
    method=f"Mean of {n} Sentinel-1 scenes, 2024, 40 m. Red VV, green VH, blue VV minus VH; colour names are a guide.",
    source="Copernicus Sentinel.", author=AUTHOR, map_share=0.6, page=(1080, 1350))
print("done")
