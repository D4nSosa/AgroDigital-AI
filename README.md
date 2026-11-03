# AgroDigital-AI

Open AgTech and geospatial toolkit for agriculture, forestry, GIS, remote sensing, agrometeorology and AI agents. It combines deterministic Python tools with an optional Model Context Protocol (MCP) server so compatible AI clients can invoke supported workflows.

It is a modular workflow layer around open data and Python—not a claim that it replaces every feature of QGIS or Google Earth Engine.

## AI-native use (v0.4)

Give an AI the repository context and attach an image or data file. For tool execution, connect the optional MCP server in an MCP-compatible client.

Install the full runtime:

~~~bash
python -m pip install -e ".[full]"
~~~

Run the MCP server:

~~~bash
agrodigital-mcp
~~~

Example client configuration: examples/mcp-config.json. Setup and usage: docs/AI_AGENT_GUIDE.md.

The AI interprets ordinary photos. AgroDigital-AI tools validate GeoJSON, inspect rasters, search STAC, download and process supported Sentinel-2 assets, and calculate supplied weather/agronomic values. An ordinary photograph is not a georeferenced raster and cannot establish soil chemistry or yield.

## Install Python core

~~~bash
python -m pip install -e .
~~~

Full optional stack and MCP:

~~~bash
python -m pip install -e ".[full]"
~~~

## Current workflows

~~~bash
agrodigital capabilities
agrodigital check-geojson examples/sample_lot.geojson
agrodigital stac-search --bbox -56 -29 -54 -27 --datetime 2026-01-01T00:00:00Z/2026-02-01T00:00:00Z --collections sentinel-2-l2a --max-items 20
agrodigital sentinel2-stac-ndvi --item-id "STAC_ITEM_ID" --output-dir ./results
agrodigital raster-info ./results/STAC_ITEM_ID_ndvi.tif
~~~

The STAC-to-NDVI command downloads the red/NIR/SCL assets for one selected public Item, derives reflectance scaling/offsets from Item metadata, aligns categorical SCL to the red/NIR grid with nearest-neighbour if needed, and calculates NDVI. Review the Item's license, date, cloud cover and output provenance. The output is a scene-level index, not a yield or crop-health measurement.

## Implemented capabilities

- GeoJSON structural checks and coordinate-range validation.
- Optional topology validation and vector reprojection with Shapely/PyProj.
- GeoTIFF metadata inspection, normalized-difference raster calculation, AOI clipping/masking and raster reprojection with Rasterio.
- Public STAC metadata search and complete Item retrieval.
- Bounded HTTPS asset download with optional SHA-256 verification.
- STAC-driven Sentinel-2 L2A red/NIR/SCL download and NDVI processing.
- Sentinel-2 NDVI from supplied aligned rasters, with independent band scale factors and offsets.
- NDVI/NDWI calculations from supplied values/arrays; GDD and rainfall calculations.
- Optional MCP server with typed tools for agent workflows.
- Unit tests and GitHub Actions.

## Important limitations

- MCP is not a universal AI connection. The client must support MCP, be configured with the server and share access to files.
- The initial MCP server is local stdio; it is not a hosted public endpoint.
- STAC scene processing uses one scene and its native red/NIR grid; no AOI clipping, temporal compositing or change detection.
- SCL nearest-neighbour alignment is categorical resampling, not advanced cloud/shadow detection.
- No atmospheric correction, Sentinel-1 processing, validated crop/yield models, automatic prescriptions or full QGIS/GEE-equivalent GUI.
- Real-scene end-to-end validation is a separate acceptance check; synthetic unit tests do not prove operational accuracy.

## Principles

Free/open core; no mandatory paid API or private key. Never fabricate data access, measurements, maps or execution. Separate observed, derived, estimated, forecast, modelled and illustrative values. Record provenance, dates, CRS, resolution, units, method, assumptions and limitations. Prefer open formats.

See SKILL.md, docs/ROADMAP.md, docs/DATA_POLICY.md, docs/AI_AGENT_GUIDE.md, and docs/modules/.

MIT License. See LICENSE.
