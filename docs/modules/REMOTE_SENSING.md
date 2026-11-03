# Remote sensing

Request AOI polygon, target dates/window, sensor, objective and acceptable spatial/temporal resolution.

## Discovery
The \`stac-search\` command queries a public STAC API (default: AWS Earth Search) by WGS84 bbox or GeoJSON intersection, date interval, collection and optional cloud-cover threshold. It returns item metadata and asset URLs. Verify collection names, catalog terms, asset availability and licensing before analysis.

## Asset download
\`download-asset\` downloads one HTTPS asset to a local file. It enforces a configurable maximum byte size, writes through a temporary file, supports optional SHA-256 verification and rejects insecure redirects. It does not implement resume, authentication, signed-URL refresh, a persistent cache or parallel downloads. Use only public/authorized asset URLs and respect provider terms.

Example:
\`\`\`bash
agrodigital download-asset "https://provider.example/path/to/B04.tif" red.tif --max-bytes 500000000
\`\`\`

## Sentinel-2 L2A NDVI
The first executable Sentinel-2 workflow accepts separate, already downloaded red (B04), NIR (B08) and optional Scene Classification Layer (SCL) GeoTIFFs. Inputs must share the exact pixel grid and CRS; the command intentionally refuses implicit resampling.

\`\`\`bash
agrodigital sentinel2-ndvi \\
  --red B04.tif --nir B08.tif --scl SCL.tif --output ndvi.tif \\
  --scale-factor 10000
\`\`\`

The scale factor and per-band offsets are explicit. Do not assume 10000 is correct for every provider/export: inspect product metadata and processing baseline first. Reflectance is calculated as DN / scale_factor + offset. SCL classes 0, 1, 3, 8, 9, 10 and 11 are excluded by default; this is a conservative class mask, not a guarantee that all cloud contamination is removed. You can override exclusions with repeated \`--exclude-scl\` options. If no SCL is supplied, cloud masking is not applied and the output states this.

This workflow does not download STAC assets automatically, unpack SAFE archives, perform atmospheric correction, resample bands, create temporal composites or process Sentinel-1. Verify band identity, scaling/offset metadata, nodata, CRS, grid alignment, acquisition time and cloud-mask suitability. NDVI is spectral contrast, not direct biomass, yield or species identification.

## Existing raster operations
With the optional Rasterio stack, inspect GeoTIFF metadata, calculate a normalized difference from two explicitly selected bands, clip/mask by GeoJSON AOI and reproject to an explicit CRS. The generic index command does not infer band mapping or preprocessing.

Validate nodata, masks, pixel alignment, CRS, resolution and value range; compare with field observations where possible.
