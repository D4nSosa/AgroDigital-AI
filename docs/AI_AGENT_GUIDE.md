# Using AgroDigital-AI with AI agents

AgroDigital-AI is designed so an AI can interpret a user's request and supplied evidence, then call deterministic tools for supported calculations and geospatial processing. The AI remains responsible for multimodal interpretation and explaining results; the toolkit is responsible for reproducible operations and metadata.

## Two ways to use it

### 1. Repository context only

Give the AI the repository URL and ask it to read SKILL.md, this guide and the relevant module documentation. Attach the image, GeoJSON, raster, soil report or weather file to the conversation.

This mode depends on the AI's own file, vision, network and code-execution tools. A repository URL does not install software or grant access to external data. If the AI cannot execute the tools, it must say so and return an evidence-aware plan rather than inventing results.

### 2. MCP-connected agent (recommended)

The optional MCP server exposes stable, typed tools to compatible AI clients. Install the package and optional dependencies in the environment that will run the MCP server:

~~~bash
python -m pip install -e ".[ai]"
~~~

Use examples/mcp-config.json as the starting point for the client's MCP configuration. The command must run in the same Python environment where AgroDigital-AI is installed. Restart or reload the MCP client after adding the server.

The MCP server currently exposes:
- agro_plan_analysis: turn a natural-language objective and evidence manifest into a workflow and missing-data checklist.
- agro_capabilities: report which optional capabilities exist in this runtime.
- agro_validate_geojson: validate an AOI geometry.
- agro_search_satellite_scenes: search public STAC metadata by EPSG:4326 bbox or GeoJSON geometry and date range.
- agro_process_sentinel2_scene: download public red/NIR/SCL assets from one STAC Item, calculate NDVI and optionally clip the result to a GeoJSON AOI.
- agro_inspect_raster: inspect raster metadata.
- agro_calculate_gdd and agro_calculate_rainfall: calculate from values explicitly supplied by the user or another trusted source.

## Working with an ordinary image

A vision-capable model should inspect the attached image itself. AgroDigital-AI does not pretend a photograph is a georeferenced raster. The agent should:
1. Describe only visible evidence (for example, apparent bare patches, canopy gaps, waterlogging indicators or image quality).
2. Ask for location/AOI and acquisition date when spatial or temporal analysis is needed.
3. Use geospatial tools only after it has a valid AOI and data source.
4. Distinguish visual interpretation from measured variables. A photograph alone cannot establish soil pH, nutrients, soil moisture, yield, cultivar or species with certainty.
5. Never claim that an image was processed by a tool unless the tool returned a checked result.

For georeferenced rasters, GeoTIFFs and GeoJSON, pass the accessible file path or structured content to the relevant tool. The MCP server and AI client must share access to those files; a file attached only inside a remote chat may not exist on the MCP server's filesystem.

## Example request

"Use AgroDigital-AI to assess this field. First inspect the attached image, then ask me for the location and date if they are missing. If I provide a GeoJSON AOI, search Sentinel-2 L2A scenes from the last growing season, choose a suitable scene transparently, calculate NDVI clipped to the lot and explain what the index can and cannot tell us. Do not estimate yield or recommend fertilizer without soil and field data."

## Compatibility and limitations

MCP is a standard interface, not universal execution. The AI client must support MCP, connect to this server, and have permission to access the relevant files. The initial release is local stdio, not a hosted public endpoint. Other AI clients can use the repository instructions and CLI if they provide an execution environment, but the project cannot guarantee compatibility with every model or chat product.

The MCP server runs where it is configured; it does not upload user files to a cloud service. Public STAC access depends on network connectivity and provider availability. This release does not include temporal composites, yield models or validated crop recommendations.
