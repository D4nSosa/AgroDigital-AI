# Roadmap

Roadmap items are targets, not claims of existing functionality.

## v0.1 foundation — complete
- [x] Modular assistant entry point and execution-mode contract.
- [x] Dependency-free GeoJSON structural validation.
- [x] NDVI/NDWI helpers from supplied values/arrays.
- [x] Basic GDD and rainfall calculations.
- [x] CLI, tests, examples and CI.

## v0.2 geospatial processing and discovery — complete
- [x] Optional raster metadata inspection, normalized difference, AOI clipping and reprojection.
- [x] GeoJSON reprojection and topology checks.
- [x] Public STAC metadata search.
- [x] CLI, docs, tests and provenance tags.

## v0.3 Sentinel-2 ingestion pipeline — implementation complete; real-scene acceptance pending
- [x] HTTPS asset download with byte ceiling, atomic write and optional SHA-256.
- [x] Complete STAC Item retrieval and asset metadata exposure.
- [x] STAC Item to red/NIR/SCL asset selection and download.
- [x] Reflectance scale/offset extraction with Earth Search BOA offset handling.
- [x] Independent red/NIR scaling and offsets.
- [x] Nearest-neighbour alignment of categorical SCL to the red/NIR grid.
- [x] NDVI output with item, source, parameter and limitation provenance.
- [x] Optional clipping of NDVI to a supplied GeoJSON AOI.
- [x] CLI workflow, unit tests and CI.
- [ ] Run and archive a real public Sentinel-2 scene end-to-end; verify scene metadata, downloaded files, grid alignment and output values independently. Synthetic tests are not a substitute for this acceptance check.

## v0.4 AI-native agent interface — implementation target
- [x] Evidence-aware analysis planning tool.
- [x] Provider-neutral agent tool functions.
- [x] Optional MCP stdio server with typed tools.
- [x] MCP client configuration example and agent usage guide.
- [x] Natural-language and multimodal input contract for image + geospatial evidence.
- [x] GeoJSON AOI input for scene search and clipped processing.
- [ ] Validate MCP handshake and tool calls in at least one real MCP client.
- [ ] Test an attached user image plus a GeoJSON AOI through a complete agent workflow.
- [ ] Add hosted/remote MCP deployment only after a concrete hosting and access-control design.

## v0.5 agroforestry and decision support
- [ ] Temporal composites, per-pixel change detection and zonal statistics.
- [ ] Sentinel-1 GRD preprocessing and comparable backscatter time series.
- [ ] Landsat search and processing.
- [ ] Weather observation/forecast adapters with source/timezone validation.
- [ ] Forest plantation monitoring and disturbance indicators.
- [ ] Explainable suitability and management-zone workflows with ground-truth requirements.

## v0.6 usable application
- [ ] Lightweight mobile web map and layer manager.
- [ ] Job progress, project files and reproducible export bundles.
- [ ] User testing with real agroforestry operations.

## v1.0 platform
- [ ] End-to-end public-data pipelines and benchmarks.
- [ ] Optional integrations and documented adapter interface.
- [ ] Reproducibility, accuracy and performance evaluation against established GIS workflows.
- [ ] Documentation and examples for Argentina and broader South America.

## Long-term boundary
AgroDigital-AI can become a capable open geospatial workbench and focused remote-sensing processing platform. Matching the full breadth of QGIS or distributed compute infrastructure of Earth Engine is a multi-year effort; avoid claiming feature parity before benchmarks and user validation.
