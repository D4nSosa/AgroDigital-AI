# GIS and spatial data

Request AOI file/location, source CRS/EPSG, target CRS, geometry type, date/version, intended scale and output format.

Workflow: inspect format, feature count, geometry, CRS, bounds and attributes; validate geometry and coordinates; reproject only when source CRS is known; select a projected CRS appropriate to the AOI for area/distance; check invalid/self-intersecting/multipart/empty geometries; export open formats with CRS and provenance.

The current agrodigital.geo validator checks structure and WGS84 longitude/latitude ranges only. It does not reproject, calculate area or validate polygon topology. Use QGIS or optional geospatial libraries for those operations.
