# GIS and spatial data

Request AOI file/location, source CRS/EPSG, target CRS, geometry type, date/version, intended scale and output format.

## Current package operations
- `check-geojson`: dependency-free structure and WGS84 coordinate-range checks.
- `vector-validate`: optional Shapely topology validation; reports invalid geometries without repairing them.
- `vector-reproject`: optional PyProj coordinate transformation with explicit source and target CRS.
- `raster-info`: inspect GeoTIFF dimensions, bands, CRS, transform, bounds, resolution, nodata and data types.
- `raster-clip`: mask/clip a raster with GeoJSON AOI.
- `raster-reproject`: warp a raster to an explicit target CRS using nearest-neighbour resampling.

Install optional dependencies with `pip install -e ".[full]"`.

## CRS and format cautions
GeoJSON coordinates are treated as WGS84 longitude/latitude under RFC 7946. For raster clipping, the AOI is transformed from EPSG:4326 to the raster CRS when needed. Never guess a source CRS. The vector reprojection helper records the target CRS in an AgroDigital-AI foreign member; projected-coordinate output is not strict RFC 7946 GeoJSON. For interoperable projected vector data, a future GeoPackage writer is preferred.

Use a projected CRS suitable for the AOI for area/distance calculations. The current package does not calculate authoritative areas, distances or topology repair. Check geometry validity, bounds, coordinate units and feature attributes before operational use.
