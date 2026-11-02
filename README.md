# AgroDigital-AI

Open AgTech and geospatial toolkit for agriculture, forestry, GIS, remote sensing and agrometeorology. The project is designed as a portable, modular alternative workflow layer around open data and Python—not as a claim that it already replaces every feature of QGIS or Google Earth Engine.

## Install

Python 3.10+.

Core only:
```bash
python -m pip install -e .
```

Optional geospatial capabilities:
```bash
python -m pip install -e ".[full]"
```

The `geo` extra provides Shapely and PyProj; `raster` provides NumPy and Rasterio. The core and STAC metadata search do not require API credentials.

## Current commands

```bash
agrodigital capabilities
agrodigital check-geojson examples/sample_lot.geojson
agrodigital gdd --tmin 12 --tmax 28 --base 10
agrodigital rainfall 12.5 0 8 3.2
agrodigital raster-info input.tif
agrodigital raster-index stack.tif ndvi.tif --band-a 4 --band-b 3 --label NDVI
agrodigital raster-clip input.tif aoi.geojson clipped.tif
agrodigital raster-reproject input.tif projected.tif --target-crs EPSG:32721
agrodigital vector-reproject lots.geojson lots_utm.geojson --source-crs EPSG:4326 --target-crs EPSG:32721
agrodigital vector-validate lots.geojson
agrodigital stac-search --bbox -56 -29 -54 -27 --datetime 2026-01-01T00:00:00Z/2026-02-01T00:00:00Z --collections sentinel-2-l2a --max-items 20
```

Use `agrodigital stac-search --help` for the full query options. STAC search returns catalog metadata and asset references; it does not download or process the imagery.

## Implemented capabilities (v0.2)

- GeoJSON structural checks and coordinate-range validation.
- Optional topology validation and vector reprojection with Shapely/PyProj.
- GeoTIFF metadata inspection, normalized-difference raster calculation, AOI clipping/masking and raster reprojection with Rasterio.
- Public STAC API search with bounding-box or GeoJSON intersection, time range, collection and cloud-cover filter.
- NDVI/NDWI calculations from supplied values/arrays; GDD and rainfall calculations.
- CLI, tests, provenance tags on generated rasters, and GitHub Actions.

## Not implemented yet

- Automatic satellite asset download, atmospheric correction, cloud/shadow masking and Sentinel-1 processing chains.
- Full QGIS-style desktop GUI, digitizing/editing, cartography/layouts, plugins or print composer.
- GEE-style distributed/cloud computation, massive image collections, interactive code editor or hosted processing backend.
- Operational weather API ingestion, terrain/hydrology toolboxes, yield models or validated variable-rate prescriptions.
- Automatic geometry repair. Topology checks report problems; they do not silently change user data.

## Principles

- Free/open core; no mandatory paid API or private key.
- Never fabricate data access, measurements, maps, or execution.
- Separate observed, derived, estimated, forecast, modelled and illustrative values.
- Record provenance, dates, CRS, resolution, units, method, assumptions and limitations.
- Portable open formats and modular, testable workflows.

Start with [SKILL.md](SKILL.md), [roadmap](docs/ROADMAP.md), [data policy](docs/DATA_POLICY.md), and the module guides under [docs/modules](docs/modules/).

MIT License. See [LICENSE](LICENSE).
