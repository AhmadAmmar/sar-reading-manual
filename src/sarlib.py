"""Shared functions: Sentinel-1 composites from Earth Engine, downloads, and the steps explained in the manual."""
import io
from pathlib import Path

import ee
import numpy as np
import rasterio
import requests

ee.Initialize(project="ee-ahmadammargeo")
ROOT = Path(__file__).resolve().parent.parent
DATA, FIG, GEN = ROOT / "data", ROOT / "figures", ROOT / "tex/generated"
for folder in (DATA, FIG, GEN):
    folder.mkdir(parents=True, exist_ok=True)


def s1(region, start, end, orbit=None):
    """Sentinel-1 ground range scenes in dual polarisation; values are already calibrated backscatter in dB."""
    c = (ee.ImageCollection("COPERNICUS/S1_GRD").filterBounds(region).filterDate(start, end)
         .filter(ee.Filter.eq("instrumentMode", "IW"))
         .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
         .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH")))
    return c.filter(ee.Filter.eq("orbitProperties_pass", orbit)) if orbit else c


def to_linear(db):
    return ee.Image(10).pow(ee.Image(db).divide(10))


def mean_db(collection, band):
    """Average in linear power and return to dB, because averaging decibels understates bright targets."""
    return collection.select(band).map(to_linear).mean().log10().multiply(10).rename(band)


def download(image, name, region, crs, scale):
    """Save an image as a GeoTIFF once; later runs reuse it. The direct route is limited to about 32 MB."""
    path = DATA / f"{name}.tif"
    if not path.exists():
        url = image.getDownloadURL(dict(region=region, crs=crs, scale=scale, format="GEO_TIFF"))
        body = requests.get(url, timeout=900).content
        if body[:2] not in (b"II", b"MM"):
            raise RuntimeError(f"{name}: {body[:300]}")
        path.write_bytes(body)
    return path


def read(path):
    with rasterio.open(path) as s:
        a = s.read().astype(float)
        if s.nodata is not None:
            a[a == s.nodata] = np.nan
        return a, s.transform, s.crs, s.bounds, list(s.descriptions)


def stretch(a, low=2, high=98):
    """Scale to 0-1 between percentiles, for display only."""
    lo, hi = np.nanpercentile(a, [low, high])
    return np.clip((a - lo) / (hi - lo), 0, 1)


def otsu(values, bins=256):
    """The threshold that best separates two groups: it maximises the variance between them (Otsu, 1979)."""
    v = values[np.isfinite(values)]
    count, edges = np.histogram(v, bins=bins)
    mids = (edges[:-1] + edges[1:]) / 2
    w = np.cumsum(count).astype(float)
    m = np.cumsum(count * mids)
    between = (m[-1] * w / w[-1] - m) ** 2 / (w * (w[-1] - w) + 1e-9) * w[-1]
    return float(mids[np.argmax(between)])
