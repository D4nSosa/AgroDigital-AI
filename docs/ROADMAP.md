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

## v0.3 bounded asset download and Sentinel-2 starter workflow — implementation complete; real-scene validation pending
- [x] HTTPS asset download with maximum-size guard, atomic temporary file and optional SHA-256 verification.
- [x] Sentinel-2 L2A NDVI from separate aligned B04/B08 rasters.
- [x] Optional SCL class masking with explicit configurable exclusions.
- [x] Explicit scale factor and per-band offsets; reject unaligned inputs.
- [x] Unit tests and CLI commands.
- [ ] Validate against a real, openly licensed Sentinel-2 scene and record product metadata, scale/offset and expected values.
- [ ] Add persistent cache, resumable transfers and robust STAC asset-selection workflow.

## v0.4 remote-sensing pipelines
- [ ] STAC item/asset selection and automated, license-aware downloads.
- [ ] SAFE/COG ingestion, product metadata parsing and scale/offset discovery.
- [ ] Cloud/shadow quality assessment and validated masking.
- [ ] Sentinel-1 GRD preprocessing and comparable backscatter time series.
- [ ] Landsat collection search and processing.
- [ ] Temporal composites, per-pixel change detection and zonal statistics.
- [ ] COG export/validation and reproducible manifests.

## v0.5 agroforestry and decision support
- [ ] Forest plantation monitoring, stand metrics and disturbance alerts.
- [ ] Field/plot time series, vegetation and water indices, seasonal summaries.
- [ ] Weather observations/forecast adapters with source/timezone validation.
- [ ] Terrain, slope, aspect, hydrology and watershed workflows.
- [ ] Management zones with ground-truth requirements and explainable methods.
- [ ] Prescription schema validation and equipment-specific exports.

## v0.6 usable application
- [ ] Lightweight web map and layer manager, optimized for mobile and low-bandwidth use.
- [ ] Local/Colab/desktop execution profiles and job progress.
- [ ] Project files, reproducible workflows and export bundles.
- [ ] User testing with real agroforestry operations.

## v1.0 platform
- [ ] End-to-end public-data pipelines and benchmarks.
- [ ] Optional integrations and a documented plugin/adapter interface.
- [ ] Reproducibility, accuracy and performance evaluation against established GIS workflows.
- [ ] Documentation and examples for Argentina and broader South America.

## Long-term boundary
AgroDigital-AI can become a capable open geospatial workbench and a focused remote-sensing processing platform. Matching the full breadth of QGIS or the distributed compute infrastructure of Earth Engine is a multi-year effort; avoid claiming feature parity before benchmarks and user validation.
