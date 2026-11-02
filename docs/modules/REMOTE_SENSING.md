# Remote sensing

Request AOI polygon, target dates/window, sensor, objective and acceptable spatial/temporal resolution.

## Discovery
The `stac-search` command queries a public STAC API (default: AWS Earth Search) by WGS84 bbox or GeoJSON intersection, date interval, collection and optional cloud-cover threshold. It returns item metadata and asset URLs. It does not download assets, authenticate, mask clouds or process imagery. Verify collection names, catalog terms, asset availability and product metadata before analysis.

Example:
```bash
agrodigital stac-search --bbox -56 -29 -54 -27 \
  --datetime 2026-01-01T00:00:00Z/2026-02-01T00:00:00Z \
  --collections sentinel-2-l2a --cloud-cover-max 30 --max-items 30
```

## Raster operations
With the optional Rasterio stack, inspect GeoTIFF metadata, calculate a normalized difference from two explicitly selected bands, clip/mask by GeoJSON AOI and reproject to an explicit CRS. The index command does not infer band mapping: the user must select the correct bands and apply correct scale factors/reflectance preprocessing.

Optical: check acquisition date, cloud/shadow masks, processing level, scale factors and band mapping. NDVI = (NIR-Red)/(NIR+Red); it is a spectral contrast, not a direct biomass or yield measurement. NDWI variants use different bands and answer different questions; always state formula and bands.

Radar: Sentinel-1 backscatter depends on acquisition geometry, polarization, moisture, roughness, vegetation structure and processing. Compare compatible/normalized acquisitions; raw backscatter is not a single physical variable.

Validate nodata, masks, pixel alignment, CRS, resolution and value range; compare with field observations where possible. The current package does not perform atmospheric correction, cloud/shadow masking, Sentinel-1 preprocessing, temporal compositing or automated satellite downloads.
