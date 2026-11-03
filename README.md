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

## Portable multipurpose Agent Skill (new)

A portable, no-server Skill is available at `skills/agrodigital-ai/`. It follows the open Agent Skills folder format and includes focused domain references plus small local Python utilities. Users attach their own lot photos, reports, boundaries and datasets directly to their chosen AI client; no user lot imagery or sample farm records are stored in this repository.

Copy or import the complete `skills/agrodigital-ai/` folder into an AI client that supports Agent Skills. A chatbot that can read Markdown can also use the instructions and references manually, but automatic discovery and script execution depend on that client's features.

The bundled scripts require Python 3.10+ and work on supplied local files only:
- `scripts/validate_geojson.py`: structural and coordinate-range validation.
- `scripts/calculate_indices.py`: NDVI and optional McFeeters NDWI from supplied CSV band values.
- `scripts/calculate_gdd.py`: GDD from supplied daily minimum/maximum temperature CSV values.

See [Skill README](skills/agrodigital-ai/README.md). Advanced raster/STAC/Sentinel-2 processing remains in the main Python package and requires a compatible execution runtime; the Skill does not create network access or install dependencies by itself.

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

The STAC-to-NDVI workflow downloads the red/NIR/SCL assets for one selected public Item, derives reflectance scaling/offsets from Item metadata, aligns categorical SCL to the red/NIR grid with nearest-neighbour if needed, and calculates NDVI. Through the Python agent API/MCP tool, the result can additionally be clipped to a supplied GeoJSON AOI. The CLI command currently processes the full scene. Review the Item's license, date, cloud cover and output provenance. The output is a scene-level index, not a yield or crop-health measurement.

## Implemented capabilities

- GeoJSON structural checks and coordinate-range validation.
- Optional topology validation and vector reprojection with Shapely/PyProj.
- GeoTIFF metadata inspection, normalized-difference raster calculation, AOI clipping/masking and raster reprojection with Rasterio.
- Public STAC metadata search and complete Item retrieval.
- Bounded HTTPS asset download with optional SHA-256 verification.
- STAC-driven Sentinel-2 L2A red/NIR/SCL download and NDVI processing, with optional GeoJSON AOI clipping through the agent API.
- Sentinel-2 NDVI from supplied aligned rasters, with independent band scale factors and offsets.
- NDVI/NDWI calculations from supplied values/arrays; GDD and rainfall calculations.
- Optional MCP server with typed tools for agent workflows.
- Unit tests, MCP SDK client handshake/tool-call test, and GitHub Actions.

## Important limitations

- MCP is not a universal AI connection. The client must support MCP, be configured with the server and share access to files.
- The initial MCP server is local stdio; it is not a hosted public endpoint.
- STAC processing handles one selected scene. It does not produce temporal composites or change detection.
- AOI clipping is available through the agent API/MCP tool; the current STAC CLI command does not expose an AOI argument.
- SCL nearest-neighbour alignment is categorical resampling, not advanced cloud/shadow detection.
- No atmospheric correction, Sentinel-1 processing, validated crop/yield models, automatic prescriptions or full QGIS/GEE-equivalent GUI.
- Real-scene end-to-end validation is a separate acceptance check; synthetic unit tests do not prove operational accuracy.
- The MCP integration test verifies protocol handshake and tool calls using the official Python SDK. An attached-image + AOI workflow still needs acceptance testing in a user-facing AI client.

## Principles

Free/open core; no mandatory paid API or private key. Never fabricate data access, measurements, maps or execution. Separate observed, derived, estimated, forecast, modelled and illustrative values. Record provenance, dates, CRS, resolution, units, method, assumptions and limitations. Prefer open formats.

See SKILL.md, docs/ROADMAP.md, docs/DATA_POLICY.md, docs/AI_AGENT_GUIDE.md, and docs/modules/.

MIT License. See LICENSE.
