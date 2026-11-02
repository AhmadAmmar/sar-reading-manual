"""The usual course of the Indus: river lines from HydroRIVERS, and how often each pixel held water, from JRC. Saved for the maps."""
import json

import ee

from sarlib import DATA, download

BOX = [67.3, 26.0, 68.6, 27.4]
region = ee.Geometry.Rectangle(BOX)
rivers = ee.FeatureCollection("WWF/HydroSHEDS/v1/FreeFlowingRivers").filterBounds(region).filter(ee.Filter.gte("DIS_AV_CMS", 500)).select(["DIS_AV_CMS", "RIV_ORD"]).getInfo()
(DATA / "indus_river_lines.geojson").write_text(json.dumps(rivers))
print(len(rivers["features"]), "segments, up to", max(f["properties"]["DIS_AV_CMS"] for f in rivers["features"]), "m3/s")
# the dry-season channel: water in at least 75% of observations, 1984 to 2021
download(ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence").unmask(0).toFloat(), "indus_occurrence_100m", region, "EPSG:32642", 100)
