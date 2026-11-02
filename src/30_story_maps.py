"""Self-explanatory story maps, 1080 by 1920, from the same analysis outputs as the manual."""
import json

import cartopy.crs as ccrs
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
    g = ax.gridlines(draw_labels=True, linewidth=0.2, color="white", alpha=0.5, x_inline=False, y_inline=False)
    g.top_labels = g.right_labels = False
    g.xlabel_style = g.ylabel_style = {"size": 5.5}
    carto.mark(ax, [(1, 67.68, 26.42), (2, 67.78, 26.73), (3, 67.86, 26.42), (4, 68.37, 26.25)], size=6.5)
    carto.scale_bar(ax, "lower right")
    pos = ax.get_position()
    carto.locator(fig, [pos.x0 + 0.02, pos.y0 + 0.012, 0.21, 0.11], [60, 78, 23, 38], (67.3, 68.6, 26.0, 27.4))


carto.story_map(FIG / "story_sindh_flood_2022", utm, sindh,
    title="Sindh under water, 2022", subtitle=f"Radar shows about {st['floodKm']:,} km² of flood in this 20,000 km² area, September 2022.\nAn unvalidated estimate: orange can include wet fields.",
    legend=[("#E69F00", "Flood: wet in 2022, not in 2021"), ("#0072B2", "Usual water"), ("#111111", "Dark both years")],
    key=[(1, "Manchar Lake", "the usual lake, with new water spreading along the western hills"), (2, "Dadu", "brighter, higher ground standing out between flooded land"), (3, "Sehwan", "hills pinch the valley, and the flood narrows"), (4, "Nawabshah", "patchy orange here may include irrigated fields")],
    method=f"Sentinel-1 radar, mean VV, 25 Aug to 15 Sep in 2021 and 2022. Smooth water returns little signal, so it looks dark. Water is below {thr} dB (Otsu threshold). Flood is wet in 2022, not in 2021, and water under 50% of the time in the JRC record. 100 m. UTM 42N.",
    source="Contains modified Copernicus Sentinel data 2021-22; JRC Global Surface Water; Natural Earth.", author=AUTHOR, map_aspect=1.07, map_share=0.47)

# London
a, _, _, b, _ = read(DATA / "london_2024_mean_40m.tif")
rgb = np.dstack([stretch(a[0]), stretch(a[1]), stretch(a[2])])
osgb = ccrs.OSGB()
ext2 = (b.left, b.right, b.bottom, b.top)
n = json.loads((DATA / "london_stats.json").read_text())["nScenesLondon"]


def london(ax, fig):
    ax.imshow(rgb, extent=ext2, origin="upper", transform=osgb, interpolation="nearest")
    ax.set_extent(ext2, osgb)
    g = ax.gridlines(draw_labels=True, linewidth=0.2, color="white", alpha=0.5)
    g.top_labels = g.right_labels = False
    g.xlabel_style = g.ylabel_style = {"size": 5.5}
    carto.mark(ax, [(1, -0.46, 51.47), (2, -0.118, 51.508), (3, -0.165, 51.507), (4, -0.02, 51.505), (5, -0.275, 51.445), (6, -0.495, 51.44)], size=6.5)
    carto.scale_bar(ax, "lower right")


carto.story_map(FIG / "story_london_radar", osgb, london,
    title="London, seen by radar", subtitle="A year of satellite radar turned into colour. It shows how surfaces\nreturn microwaves, and not what the eye would see.",
    legend=[("#E8F050", "Yellow: dense buildings"), ("#D070E8", "Pink: built-up"), ("#5F9F2F", "Green: vegetation"), ("#000080", "Blue: water")],
    key=[(1, "Heathrow", "runways look dark and smooth among bright buildings"), (2, "River Thames", "calm water reflects the signal away, so it looks dark"), (3, "Hyde Park", "a dark gap in the city, because grass returns little"), (4, "Canary Wharf", "towers form corners, which give the strongest returns"), (5, "Richmond Park", "open grassland, with a low return"), (6, "Reservoir", "still water, among the darkest surfaces here")],
    method=f"Mean of {n} Sentinel-1 ascending scenes, 2024, averaged in linear power. Red is VV, green is VH, blue is VV minus VH, each stretched between its 2nd and 98th percentiles. Colour names are a guide. 40 m. British National Grid.",
    source="Contains modified Copernicus Sentinel data 2024, via Google Earth Engine.", author=AUTHOR, map_aspect=0.75, map_share=0.38)
print("done")
