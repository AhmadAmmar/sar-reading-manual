# Reading radar images

A working manual for reading Sentinel-1 radar images, step by step, on real places. LaTeX is the one source for the PDF and the web pages, and every number and map comes from the code here.

![Flood water in Sindh in September 2022, mapped from radar](figures/map_sindh_flood_2022.png)

![London in radar, 2024](figures/map_london_false_colour.png)

## Chapters

1. How to read a radar image: London
2. Mapping a flood: Sindh, 2022

Planned next, built from real runs in [kkh-hazard](https://github.com/AhmadAmmar/kkh-hazard) on the Karakoram Highway:

3. Heights from phase: a DEM from a Sentinel-1 pair over Hunza (HyP3, phase to height, SNAPHU TOPO), checked against Copernicus GLO-30 and Google GEM-15
4. Moving slopes: NISAR L-band interferograms and pixel offsets over landslides along the highway (SNAPHU DEFO, velocity)
5. Covariance and polarimetry: NISAR GCOV over the corridor, masks, dual-pol ratios and full-pol decompositions

Then forests, urban growth, ships, ice, conflict damage and subsidence.

## Rebuild

```bash
cd src
python 01_london_basics.py
python 02_sindh_flood.py
python 20_manual_inputs.py
cd ../tex
pdflatex main && pdflatex main
```

The Python scripts need an authenticated Earth Engine account, and `research-helpers`. The same exports for the Earth Engine Code Editor are in [earth-engine-code](https://github.com/AhmadAmmar/earth-engine-code/tree/main/scripts/sar).

Each map has a `.map.json` record of its sources and projection.

## Credit

Contains modified Copernicus Sentinel data. JRC Global Surface Water. Code under MIT, and text and maps under CC BY 4.0.
