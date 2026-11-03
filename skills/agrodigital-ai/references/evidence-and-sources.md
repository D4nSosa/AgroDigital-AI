# Evidence, sources and uncertainty

## Evidence labels
Use explicit labels:
- **Observed:** directly visible in a supplied image or file.
- **Measured:** recorded by an instrument, laboratory, station or source dataset.
- **Calculated:** derived reproducibly from supplied/verified inputs.
- **Retrieved:** obtained from an external catalog or source during this session.
- **Estimated/modelled:** produced by a model with stated assumptions.
- **Forecast:** future-oriented source output, not an observation.
- **Hypothesis:** plausible explanation not yet confirmed.
- **Illustrative:** example or mock-up, never a real measurement.

## Provenance
For external geospatial/climate data, record provider, product/collection, item/station ID, acquisition or valid time, access date, spatial and temporal resolution, CRS, units, scale/offset, cloud/nodata handling, processing method and source link where available.

## Source hierarchy
Prefer official data providers, scientific institutions, government agencies, peer-reviewed literature and product documentation. Check source date, geographic coverage, license and methodology. Community content may provide context but should not be the sole basis for high-consequence claims.

## Uncertainty
Name the uncertainty that matters: missing data, low resolution, mixed pixels, clouds, seasonal effects, uncertain location/date, unknown sampling depth, uncalibrated model or ambiguous image. Avoid generic disclaimers that do not help the user.

## Contradictions
If user records and external sources disagree, show the discrepancy, dates and units. Do not silently choose one. Ask which source is authoritative only when the conflict blocks the requested conclusion.
