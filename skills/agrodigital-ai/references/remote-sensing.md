# Remote sensing and satellite analysis

## Sensor choice
- Sentinel-2 / optical: multispectral surface reflectance for vegetation, water and land-cover indicators; affected by clouds, haze, shadows, season and viewing geometry.
- Sentinel-1 / SAR: radar backscatter useful under cloud cover and for structural/moisture-related change; requires orbit, polarization, incidence angle, terrain and preprocessing awareness.
- Landsat: optical multispectral observations with a longer historical record and different spatial/temporal characteristics.
- UAV/drone imagery: potentially high spatial detail; requires orthomosaic/georeferencing and acquisition metadata for spatial measurement.

## Indices
- NDVI = (NIR - Red) / (NIR + Red)
- NDWI (McFeeters) = (Green - NIR) / (Green + NIR)
- NDMI = (NIR - SWIR) / (NIR + SWIR)

Always state the exact index variant and bands used. Check reflectance scaling/offset, nodata, zero denominators, cloud/shadow masks, pixel alignment and sensor product level. Index values are unitless. Do not compare products blindly when processing, sensor, season or atmosphere differs.

## Time series
Use consistent AOI, sensor/product, index definition, cloud masking, compositing window and spatial aggregation. Report the number of valid observations per period. A gap in observations is not evidence of no change. Separate seasonality from disturbance or management effects.

## Sentinel-2 AgroDigital-AI package boundary
The existing v0.4 workflow searches public STAC metadata and processes one selected Sentinel-2 L2A Item: downloads red/NIR and optional SCL assets, applies metadata scale/offset, aligns categorical SCL with nearest-neighbour when needed, calculates NDVI and can clip to a supplied GeoJSON AOI through the agent API. It does not provide atmospheric correction, robust cloud/shadow masking, temporal composites, yield models or Sentinel-1 processing.

## Interpretation
Describe spatial/temporal patterns, not unsupported causes. A low index may reflect bare soil, crop stage, harvest, water stress, clouds/shadows, soil background or other factors. Use ground truth before operational recommendations.
