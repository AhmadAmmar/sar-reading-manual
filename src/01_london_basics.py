"""Chapter 1: how to read radar, on London. One scene against a year's mean, each polarisation, and a false-colour map with places marked."""
import json

import cartopy.crs as ccrs
import ee
import matplotlib.pyplot as plt
import numpy as np

from research_helpers import carto
from sarlib import DATA, FIG, GEN, download, mean_db, read, s1, stretch

carto.use_style()
BOX = [-0.60, 51.30, 0.25, 51.70]
ZOOM = [-0.20, 51.46, -0.05, 51.53]
region, zoom = ee.Geometry.Rectangle(BOX), ee.Geometry.Rectangle(ZOOM)
col = s1(region, "2024-01-01", "2025-01-01", "ASCENDING")
n_scenes = col.size().getInfo()
vv, vh = mean_db(col, "VV"), mean_db(col, "VH")
ratio = vv.subtract(vh).rename("VV_VH")
mean = download(vv.addBands(vh).addBands(ratio).toFloat(), "london_2024_mean_40m", region, "EPSG:27700", 40)
single = col.filter(ee.Filter.contains(leftField=".geo", rightValue=zoom)).first()  # a scene that covers the whole patch
scene_date = single.date().format("YYYY-MM-dd").getInfo()
one = download(single.select("VV").toFloat(), "london_single_vv_10m", zoom, "EPSG:27700", 10)
many = download(vv.toFloat(), "london_mean_vv_10m", zoom, "EPSG:27700", 10)

a, tr, crs, b, _ = read(mean)
proj = ccrs.OSGB()
extent = (b.left, b.right, b.bottom, b.top)
rgb = np.dstack([stretch(a[0]), stretch(a[1]), stretch(a[2])])
PLACES = [(1, -0.46, 51.47, "Heathrow Airport"), (2, -0.118, 51.508, "River Thames, central London"), (3, -0.165, 51.507, "Hyde Park"), (4, -0.02, 51.505, "Canary Wharf"), (5, -0.275, 51.445, "Richmond Park"), (6, -0.495, 51.44, "Reservoir south-west of Heathrow")]
fig = plt.figure(figsize=carto.size("double", 0.66))
ax = fig.add_subplot(projection=proj)
ax.imshow(rgb, extent=extent, origin="upper", transform=proj, interpolation="nearest")
ax.set_extent(extent, proj)
g = ax.gridlines(draw_labels=True, linewidth=0.2, color="white", alpha=0.5)
g.top_labels = g.right_labels = False
g.xlabel_style = g.ylabel_style = {"size": 6.5}
carto.mark(ax, [(n, x, y) for n, x, y, _ in PLACES])
carto.scale_bar(ax, "lower right")
carto.locator(fig, [0.14, 0.60, 0.16, 0.26], [-11, 3, 49.5, 59.5], (BOX[0], BOX[2], BOX[1], BOX[3]))
carto.credit(fig, f"Contains modified Copernicus Sentinel data 2024 ({n_scenes} ascending scenes), Google Earth Engine")
carto.finish_map(fig, FIG / "map_london_false_colour", title="London in radar, 2024", sources=["Copernicus Sentinel-1 GRD via Earth Engine"], crs="British National Grid, EPSG:27700")
plt.close(fig)

fig, ax = plt.subplots(1, 3, figsize=carto.size("double", 0.36))
for x, band, name in zip(ax, a, ("VV (dB)", "VH (dB)", "VV minus VH (dB)")):
    im = x.imshow(band, cmap=carto.SEQUENTIAL, vmin=np.nanpercentile(band, 2), vmax=np.nanpercentile(band, 98), extent=extent)
    x.set_title(name)
    x.set_axis_off()
    fig.colorbar(im, ax=x, shrink=0.75, orientation="horizontal", pad=0.03)
carto.panel_labels(ax)
carto.finish_map(fig, FIG / "fig_london_bands", title="London by polarisation", sources=["Copernicus Sentinel-1 GRD via Earth Engine"], crs="British National Grid, EPSG:27700", scale_bar="Same extent as the map of London, shown for comparison of bands.")
plt.close(fig)

u, _, _, _, _ = read(one)
m, _, _, _, _ = read(many)
fig, ax = plt.subplots(1, 3, figsize=carto.size("double", 0.36))
h, w = min(u.shape[1], m.shape[1]), min(u.shape[2], m.shape[2])
ax[0].imshow(u[0], cmap="gray", vmin=-25, vmax=5)
ax[0].set_title(f"One scene, {scene_date}")
ax[1].imshow(m[0], cmap="gray", vmin=-25, vmax=5)
ax[1].set_title(f"Mean of {n_scenes} scenes")
ax[2].hist(u[0][np.isfinite(u[0])], bins=120, range=(-30, 15), alpha=0.65, label="One scene", color=carto.QUALITATIVE[1])
ax[2].hist(m[0][np.isfinite(m[0])], bins=120, range=(-30, 15), alpha=0.65, label="Mean", color=carto.QUALITATIVE[0])
ax[2].set_xlabel("VV (dB)")
ax[2].set_ylabel("Pixels")
ax[2].legend()
ax[0].set_axis_off()
ax[1].set_axis_off()
carto.panel_labels(ax)
fig.tight_layout()
carto.finish_map(fig, FIG / "fig_london_speckle", title="Speckle in central London", sources=["Copernicus Sentinel-1 GRD via Earth Engine"], crs="British National Grid, EPSG:27700", scale_bar="Panels show about 10 by 8 km; the graph has no scale.")
plt.close(fig)

water = a[0] < -15
# speckle is measured over the most uniform 300 m patch in the mean image, because a city's overall spread is mostly real differences
from scipy.ndimage import uniform_filter
h = min(u.shape[1], m.shape[1]); w_ = min(u.shape[2], m.shape[2])
U, M = u[0][:h, :w_], m[0][:h, :w_]
ok = np.isfinite(U) & np.isfinite(M)
var = uniform_filter(np.nan_to_num(M) ** 2, 30) - uniform_filter(np.nan_to_num(M), 30) ** 2
var[uniform_filter(ok.astype(float), 30) < 1] = np.inf
r, c = np.unravel_index(np.argmin(var), var.shape)
enl = lambda d: (lambda x: round(float(np.nanmean(x) ** 2 / np.nanvar(x)), 1))(10 ** (d[r - 15:r + 15, c - 15:c + 15] / 10))
stats = dict(enlOne=enl(U), enlMany=enl(M), nScenesLondon=n_scenes, sceneDate=scene_date, stdOne=round(float(np.nanstd(U[r - 15:r + 15, c - 15:c + 15])), 2), stdMany=round(float(np.nanstd(M[r - 15:r + 15, c - 15:c + 15])), 2))
sample = {}
pts = {name: (x, y) for _, x, y, name in PLACES}
coords = ee.FeatureCollection([ee.Feature(ee.Geometry.Point(v).buffer(60), {"place": k}) for k, v in pts.items()])
got = vv.addBands(vh).addBands(ratio).reduceRegions(coords, ee.Reducer.mean(), 10).getInfo()["features"]
rows = [(f["properties"]["place"], f"{f['properties']['VV']:.1f}", f"{f['properties']['VH']:.1f}", f"{f['properties']['VV_VH']:.1f}") for f in got]
(GEN / "london_places.tex").write_text("\\begin{tabular}{lrrr}\n\\toprule\nPlace & VV (dB) & VH (dB) & VV minus VH \\\\\n\\midrule\n" + "\n".join(" & ".join(r) + r" \\" for r in rows) + "\n\\bottomrule\n\\end{tabular}\n", encoding="utf8")
(DATA / "london_stats.json").write_text(json.dumps(stats))
print(stats, rows)
