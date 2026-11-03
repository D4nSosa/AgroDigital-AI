# Remote sensing

Request AOI polygon, target dates/window, sensor, objective and acceptable spatial/temporal resolution.

## Discovery
The stac-search command queries a public STAC API (default: AWS Earth Search) by WGS84 bbox or GeoJSON intersection, date interval, collection and optional cloud-cover threshold. Results include Item IDs, asset references and raster metadata where supplied. Verify collection names, catalog terms, asset availability and licensing before analysis.

## Asset download
download-asset downloads one HTTPS asset to a local file. It enforces a configurable maximum byte size, writes through a temporary file, supports optional SHA-256 verification and rejects insecure redirects. It does not implement resume, authentication, signed-URL refresh, a persistent cache or parallel downloads. Use only public/authorized asset URLs and respect provider terms.

## Sentinel-2 L2A NDVI from supplied rasters
The explicit sentinel2-ndvi command accepts separate, already downloaded red (B04), NIR (B08) and optional SCL GeoTIFFs. Red and NIR must share the exact pixel grid and CRS. Independent scale factors and offsets can be supplied. Reflectance is calculated as DN / band_scale_factor + offset.

## STAC Item to NDVI
For supported public STAC Items, the integrated command performs discovery-to-processing for one selected Item:

~~~bash
agrodigital sentinel2-stac-ndvi --item-id "STAC_ITEM_ID" --output-dir ./results
~~~

It selects red/NIR and optional SCL assets, downloads them with byte limits and HTTPS-only redirects, reads scale/offset metadata and writes NDVI with provenance. It handles Earth Search BOA offset metadata and baseline metadata; if a red/NIR asset has no scale metadata, it fails rather than guessing. If SCL uses a different grid (commonly a coarser categorical grid), it is aligned to the red/NIR grid using nearest-neighbour resampling.

This is one-scene processing on the red/NIR grid. It does not clip to a user AOI, build temporal composites, perform atmospheric correction or guarantee cloud-free pixels. Review item date, cloud cover, asset metadata, license, output grid and values. NDVI is spectral contrast, not direct biomass, yield, soil moisture or species identification.

## Existing raster operations
With the optional Rasterio stack, inspect GeoTIFF metadata, calculate a normalized difference from two explicitly selected bands, clip/mask by GeoJSON AOI and reproject to an explicit CRS. The generic index command does not infer band mapping or preprocessing.

Validate nodata, masks, pixel alignment, CRS, resolution and value range; compare with field observations where possible.
