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

## Formats
- GeoJSON: vector geometry and properties.
- GeoPackage: multi-layer vector container.
- GeoTIFF/COG: raster data.
- CSV: tabular values; spatial columns need explicit CRS.
- KML/KMZ: visualization-oriented vector data.
- NetCDF/Zarr: multidimensional scientific data.

## Area and distance
Use a suitable projected CRS or geodesic calculation. State units and method. Validate geometry before measurement.
