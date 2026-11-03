# Geospatial data and GIS

## Coordinate reference systems
- Identify CRS from embedded metadata or explicit user information; never guess silently.
- GeoJSON coordinates are normally WGS84 longitude, latitude (EPSG:4326) unless otherwise documented.
- Confirm axis order and coordinate units before calculations.
- Reproject to an appropriate local projected CRS before measuring area/distance. Do not calculate accurate area directly from degrees.
- Record source CRS, target CRS, transformation and resampling.

## Geometry
Inspect geometry type, feature count, coordinate ranges, validity, self-intersections, empty geometries and duplicate features. Do not silently repair a polygon. If repair is necessary, preserve original and report the repair method.

## Raster
Inspect dimensions, band count, data type, CRS, transform, pixel size, nodata, scale/offset, units, compression and bounds. Check alignment before pixel-wise operations. Categorical rasters require nearest-neighbour resampling; continuous data may use an appropriate continuous resampler.

## Zonal analysis
Confirm that AOI and raster overlap, CRS match, pixel inclusion rule is stated and nodata/cloud masks are handled. Report valid pixel count and coverage fraction. Do not imply a polygon statistic represents unobserved areas.

## Management zones and prescription maps
- A management-zone layer represents spatial classes for a defined management purpose; document the target operation and variables used.
- Use appropriate projected CRS, topology checks, minimum mapping unit, polygon sliver review, boundary clipping and NoData treatment.
- For raster-derived zones, document pixel size, resampling, mask, classification method and class thresholds. Do not imply sub-pixel precision.
- A prescription layer must include an explicit rate field, units, target operation/input, valid range, NoData behavior and metadata. Do not create rates from zone IDs alone.
- Before machine use, verify controller/vendor format, coordinate system, field boundary, rate units, file encoding, grid/cell size, legends and machine calibration. Export to a generic format (GeoPackage, GeoJSON, CSV or GeoTIFF) only when appropriate; proprietary controller formats require their own specification.
- Preserve an auditable source-to-output trail and keep draft files separate from approved operational files.

## Raster
Inspect dimensions, band count, data type, CRS, transform, pixel size, nodata, scale/offset, units, compression and bounds. Check alignment before pixel-wise operations. Categorical rasters require nearest-neighbour resampling; continuous data may use an appropriate continuous resampler.

## Formats
- GeoJSON: vector geometry and properties.
- GeoPackage: multi-layer vector container.
- GeoTIFF/COG: raster data.
- CSV: tabular values; spatial columns need explicit CRS.
- KML/KMZ: visualization-oriented vector data.
- NetCDF/Zarr: multidimensional scientific data.

## Area and distance
Use a suitable projected CRS or geodesic calculation. State units and method. Validate geometry before measurement.
