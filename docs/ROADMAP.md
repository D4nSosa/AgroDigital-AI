# Roadmap

Roadmap items are targets, not claims of existing functionality.

## v0.1 foundation — complete
- [x] Modular assistant entry point and execution-mode contract.
- [x] Dependency-free GeoJSON structural validation.
- [x] NDVI/NDWI helpers from supplied values/arrays.
- [x] Basic GDD and rainfall calculations.
- [x] CLI, tests, examples and CI.

## v0.2 geospatial processing and discovery — implementation in progress
- [x] Optional raster metadata inspection with Rasterio.
- [x] Normalized-difference GeoTIFF generation from selected input bands.
- [x] Raster clipping/masking by GeoJSON AOI.
- [x] Raster reprojection to an explicit CRS.
- [x] GeoJSON reprojection with PyProj and topology checks with Shapely.
- [x] Public STAC catalog search without credentials.
- [x] CLI and metadata/provenance tags.
- [ ] Validate optional workflows against real openly licensed satellite scenes and expand integration tests.

## v0.3 remote-sensing pipelines
- [ ] Safe asset download/cache manager with checksums, size limits and resumable transfers.
- [ ] Sentinel-2 L2A band selection, scale-factor handling and cloud/shadow masking.
- [ ] Sentinel-1 GRD preprocessing and comparable backscatter time series.
- [ ] Landsat collection search and processing.
- [ ] Temporal composites, per-pixel change detection and zonal statistics.
- [ ] Reproducible output manifests and COG export/validation.

## v0.4 agroforestry and decision support
- [ ] Forest plantation monitoring, stand metrics and disturbance alerts.
- [ ] Field/plot time series, vegetation and water indices, seasonal summaries.
- [ ] Weather observations/forecast adapters with source/timezone validation.
- [ ] Terrain, slope, aspect, hydrology and watershed workflows.
- [ ] Management zones with ground-truth requirements and explainable methods.
- [ ] Prescription schema validation and equipment-specific exports.

## v0.5 usable application
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
