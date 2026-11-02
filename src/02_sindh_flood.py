"""Chapter 2: mapping the 2022 Sindh flood. A dry year against the flood, a threshold from the data, permanent water removed."""
import json

import cartopy.crs as ccrs
import ee
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from research_helpers import carto
from sarlib import DATA, FIG, download, mean_db, otsu, read, s1, stretch

carto.use_style()
BOX = [67.3, 26.0, 68.6, 27.4]
region = ee.Geometry.Rectangle(BOX)
CRS, SCALE = "EPSG:32642", 100
PRE, POST = ("2021-08-25", "2021-09-15"), ("2022-08-25", "2022-09-15")
pre_c, post_c = s1(region, *PRE), s1(region, *POST)
n_pre, n_post = pre_c.size().getInfo(), post_c.size().getInfo()
pre, post = mean_db(pre_c, "VV").rename("pre"), mean_db(post_c, "VV").rename("post")
occurrence = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence").unmask(0).rename("occurrence")
path = download(pre.addBands(post).addBands(occurrence).toFloat(), "sindh_flood_100m", region, CRS, SCALE)
a, tr, crs, b, _ = read(path)
before, after, occ = a
thr = otsu(after)
wet_after, wet_before = after < thr, before < thr
flood = wet_after & ~wet_before & (occ < 50)
permanent = wet_after & (occ >= 50)
cell = SCALE * SCALE / 1e6
stats = dict(nPre=n_pre, nPost=n_post, threshold=round(thr, 1), floodKm=int(flood.sum() * cell), wetBeforeKm=int(wet_before.sum() * cell), wetAfterKm=int(wet_after.sum() * cell), permanentKm=int(permanent.sum() * cell), scanKm=int(np.isfinite(after).sum() * cell))
for off in (-2, 2):
    stats[f"floodKm{'Low' if off < 0 else 'High'}"] = int((((after < thr + off) & ~(before < thr + off) & (occ < 50)).sum()) * cell)
(DATA / "sindh_stats.json").write_text(json.dumps(stats))
print(stats)

proj = ccrs.UTM(42)
extent = (b.left, b.right, b.bottom, b.top)
PLACES = [(1, 67.68, 26.42, "Manchar Lake"), (2, 67.78, 26.73, "Dadu"), (3, 67.86, 26.42, "Sehwan"), (4, 68.37, 26.25, "Nawabshah")]

fig, ax = plt.subplots(1, 3, figsize=carto.size("double", 0.42), subplot_kw={"projection": proj})
for x, im_, t in zip(ax, (before, after), ("September 2021", "September 2022")):
    x.imshow(im_, cmap="gray", vmin=-22, vmax=-2, extent=extent, origin="upper", transform=proj)
    x.set_title(t)
    x.set_extent(extent, proj)
ax[2].imshow(np.dstack([stretch(before, 1, 99), stretch(after, 1, 99), stretch(after, 1, 99)]), extent=extent, origin="upper", transform=proj)
ax[2].set_title("Red: lost signal in 2022")
ax[2].set_extent(extent, proj)
carto.panel_labels(ax)
carto.finish_map(fig, FIG / "fig_sindh_before_after", title="Sindh before and during the flood", sources=["Copernicus Sentinel-1 GRD via Earth Engine"], crs="UTM 42N, EPSG:32642", scale_bar="Panels share the extent and scale bar of the flood map.")
plt.close(fig)

fig, ax = plt.subplots(figsize=carto.size("single", 0.62))
ax.hist(after[np.isfinite(after)], bins=150, range=(-30, 5), color=carto.QUALITATIVE[0])
ax.axvline(thr, color=carto.QUALITATIVE[5], lw=1.2)
ax.text(thr - 0.4, ax.get_ylim()[1] * 0.9, f"Threshold {thr:.1f} dB", ha="right", fontsize=7, color=carto.QUALITATIVE[5])
ax.set_xlabel("VV backscatter, September 2022 (dB)")
ax.set_ylabel("Pixels")
carto.save(fig, FIG / "fig_sindh_histogram")
plt.close(fig)

cls = np.full(after.shape, np.nan)
cls[np.isfinite(after)] = 0
cls[permanent] = 1
cls[flood] = 2
fig = plt.figure(figsize=carto.size("double", 0.92))
ax = fig.add_subplot(projection=proj)
ax.imshow(stretch(after, 2, 98), cmap="gray", extent=extent, origin="upper", transform=proj)
ax.imshow(np.ma.masked_where(cls == 0, cls), cmap=ListedColormap(["#0072B2", "#E69F00"]), vmin=1, vmax=2, extent=extent, origin="upper", transform=proj, interpolation="nearest")
ax.set_extent(extent, proj)
g = ax.gridlines(draw_labels=True, linewidth=0.2, color="white", alpha=0.5)
g.top_labels = g.right_labels = False
g.xlabel_style = g.ylabel_style = {"size": 6.5}
rivers = gpd.read_file(DATA / "indus_river_lines.geojson")
ax.add_geometries(rivers.geometry, ccrs.PlateCarree(), facecolor="none", edgecolor="white", linewidth=1.6, zorder=8)
ax.add_geometries(rivers.geometry, ccrs.PlateCarree(), facecolor="none", edgecolor="#00E5FF", linewidth=0.8, zorder=9)
carto.mark(ax, [(n, x, y) for n, x, y, _ in PLACES])
carto.scale_bar(ax, "lower right")
ax.legend([plt.Rectangle((0, 0), 1, 1, color="#E69F00"), plt.Rectangle((0, 0), 1, 1, color="#0072B2"), plt.Line2D([0], [0], color="#00E5FF", lw=1.2)], ["Flood, not wet in 2021", "Usual water", "Mapped river course"], loc="upper left", fontsize=7, frameon=True)
carto.locator(fig, [0.17, 0.13, 0.17, 0.18], [60, 78, 23, 38], (BOX[0], BOX[2], BOX[1], BOX[3]))
carto.credit(fig, "Contains modified Copernicus Sentinel data 2021-2022; JRC Global Surface Water")
carto.finish_map(fig, FIG / "map_sindh_flood_2022", title="Flood water in Sindh, September 2022", sources=["Copernicus Sentinel-1 GRD via Earth Engine", "JRC Global Surface Water 1.4", "HydroRIVERS via Free Flowing Rivers"], crs="UTM 42N, EPSG:32642", boundary_note=False, note=f"Threshold {thr:.1f} dB from Otsu; area {stats['floodKm']} km2, not validated against field or optical data.")
plt.close(fig)
