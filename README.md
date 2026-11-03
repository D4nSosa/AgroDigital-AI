# AgroDigital-AI

Open AgTech and geospatial toolkit for agriculture, forestry, GIS, remote sensing and agrometeorology. The project is a portable, modular alternative workflow layer around open data and Python—not a claim that it replaces every feature of QGIS or Google Earth Engine.

## Install
Python 3.10+.

Core:
\`\`\`bash
python -m pip install -e .
\`\`\`
Full optional geospatial stack:
\`\`\`bash
python -m pip install -e ".[full]"
\`\`\`

## Current workflows
\`\`\`bash
agrodigital capabilities
agrodigital check-geojson examples/sample_lot.geojson
agrodigital stac-search --bbox -56 -29 -54 -27 --datetime 2026-01-01T00:00:00Z/2026-02-01T00:00:00Z --collections sentinel-2-l2a --max-items 20
agrodigital download-asset "https://provider.example/path/B04.tif" B04.tif --max-bytes 500000000
agrodigital sentinel2-ndvi --red B04.tif --nir B08.tif --scl SCL.tif --output ndvi.tif --scale-factor 10000
agrodigital raster-info ndvi.tif
\`\`\`
The download example uses a placeholder URL; replace it with an authorized asset URL returned by a catalog/provider. STAC discovery returns metadata and asset references; it does not automatically download a selected item.

## Implemented capabilities
- GeoJSON structural checks and coordinate-range validation.
- Optional topology validation and vector reprojection with Shapely/PyProj.
- GeoTIFF metadata inspection, normalized-difference raster calculation, AOI clipping/masking and raster reprojection with Rasterio.
- Public STAC API search by bbox or GeoJSON intersection, date, collection and cloud-cover metadata.
- Bounded HTTPS asset download with optional SHA-256 verification.
- Sentinel-2 L2A NDVI from separate, aligned red/NIR GeoTIFFs, with optional SCL class masking and explicit scale/offset parameters.
- NDVI/NDWI calculations from supplied values/arrays; GDD and rainfall calculations.
- CLI, unit tests, provenance tags and GitHub Actions.

## Important limitations
- No automatic STAC item/asset selection, SAFE archive unpacking, signed-URL refresh, persistent cache or resumable downloads.
- Sentinel-2 inputs must already be downloaded and aligned; scale factor and offsets must be checked against source metadata.
- SCL masking is class-based and does not guarantee cloud-free pixels.
- No atmospheric correction, advanced cloud/shadow algorithm, Sentinel-1 processing, temporal composites or COG generation.
- No full QGIS-style desktop GUI or GEE-style distributed compute.
- No automatic geometry repair.

## Principles
Free/open core; no mandatory paid API or private key. Never fabricate data access, measurements, maps or execution. Separate observed, derived, estimated, forecast, modelled and illustrative values. Record provenance, dates, CRS, resolution, units, method, assumptions and limitations. Prefer open formats and reproducible workflows.

See [SKILL.md](SKILL.md), [roadmap](docs/ROADMAP.md), [data policy](docs/DATA_POLICY.md), and the module guides under [docs/modules](docs/modules/).

MIT License. See [LICENSE](LICENSE).
