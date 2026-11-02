# Remote sensing

Request AOI polygon, target dates/window, sensor, objective and acceptable spatial/temporal resolution.

Optical: check acquisition date, cloud/shadow masks, processing level, scale factors and band mapping. NDVI = (NIR-Red)/(NIR+Red); it is a spectral contrast, not a direct biomass or yield measurement. NDWI variants use different bands and answer different questions; always state formula and bands.

Radar: Sentinel-1 backscatter depends on acquisition geometry, polarization, moisture, roughness, vegetation structure and processing. Compare compatible/normalized acquisitions; raw backscatter is not a single physical variable.

Validate nodata, masks, pixel alignment, CRS, resolution and value range; compare with field observations where possible. The current indices module computes NDVI/NDWI from supplied reflectance values/arrays. It does not download imagery, correct atmospherics, mask clouds or read GeoTIFF files.
