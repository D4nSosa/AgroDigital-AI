# Tool selection and execution

This reference explains what the Skill can do in different environments. Always check actual capabilities before choosing a path.

## Mode A — Native chatbot tools

Use the chatbot's own file upload, vision, spreadsheet, code execution, chart and document-generation features when available. This is the most portable mode and does not require a dedicated AgroDigital server.

- Photos: use native vision; describe visible evidence.
- CSV/XLSX: inspect columns, units, dates, missing values and calculate with available data tools.
- GeoJSON: parse and validate geometry; calculate area only after confirming coordinate system and method.
- GeoTIFF: requires a raster-capable runtime such as Rasterio/GDAL or equivalent.
- PDF reports: extract text/tables; inspect page images if scan-based.
- Charts: use actual user data, label units and periods, and do not invent values.

## Mode B — Bundled scripts

Scripts in this Skill are small, deterministic helpers:
- `scripts/validate_geojson.py`: standard-library GeoJSON structural and coordinate-range checks.
- `scripts/calculate_indices.py`: calculate NDVI and NDWI from CSV columns of supplied band values.
- `scripts/calculate_gdd.py`: calculate daily GDD from supplied Tmin/Tmax CSV values.

Run `python scripts/<script>.py --help` first. Scripts read user-supplied files and write outputs only to the requested path. They do not download remote data.

## Mode C — AgroDigital-AI Python package

If the package is installed in the current runtime, use its existing CLI/API for supported tasks. Install instructions are in the repository README. The full optional stack includes NumPy, Shapely, PyProj, Rasterio and MCP.

Existing package capabilities documented in v0.4:
- GeoJSON validation; optional topology checks and coordinate transformation.
- GeoTIFF inspection, normalized-difference raster calculations, AOI clipping and reprojection.
- Public STAC metadata search.
- Sentinel-2 L2A red/NIR/optional SCL asset download and single-scene NDVI processing, including optional AOI clipping through the agent API.
- GDD and rainfall calculations from supplied values.
- Optional local MCP stdio tools for MCP-compatible clients.

Do not imply these functions are available unless the package and dependencies are installed and the tool/runtime can access the relevant files.

## File access rules

- Confirm the exact input path and output path.
- Never overwrite user data unless explicitly requested.
- Preserve original files; write derived outputs separately.
- Keep diagnostics separate from machine-readable output where possible.
- Record command, parameters, package version and output path.
- If the chatbot attachment is not visible to the script runtime, explain the limitation instead of inventing a local path.

## Network and remote sensing

A repository URL does not provide network access to the current runtime. Before external catalog or weather queries, verify that web/network tools are available. If unavailable, request a user-provided export or give a reproducible workflow without claiming it ran.
