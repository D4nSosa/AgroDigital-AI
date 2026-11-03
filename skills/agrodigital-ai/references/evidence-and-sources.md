# Evidence and sources

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

## Execution labels
For code, scripts and external tools, also state one of:
- **EXECUTED_ORIGINAL:** the original repository script/tool was accessible and actually run; identify path/version and inputs.
- **EXECUTED_ALTERNATIVE:** a different implementation was actually run; identify path and differences. Do not claim equivalence without comparison.
- **CODE_ONLY:** code was shown or written but not executed.
- **CONCEPTUAL:** only a workflow or method was described.
- **RETRIEVED:** a live source was queried and returned data; retain identifiers and retrieval time.
- **ILLUSTRATIVE:** synthetic output, clearly separated from observations.

A repository link, source document, copied code, plausible terminal output or an assistant's assertion is not execution evidence. Do not invent paths, command output, package versions, API responses or file creation. When feasible, retain command, exit status, relevant stdout/stderr and input/output filenames. If the runtime cannot expose logs, state that limitation.

## Provenance
For external geospatial/climate data, record provider, product/collection, item/station ID, acquisition or valid time, access date, spatial and temporal resolution, CRS, units, scale/offset, cloud/nodata handling, processing method and source link where available.

For prescription and management-zone outputs, additionally record source layers, sampling dates/depths, crop/operation, classification or rate logic, units, thresholds, field validation, machine/controller target and approval status.

## Source hierarchy
Prefer official data providers, scientific institutions, government agencies, peer-reviewed literature and product documentation. Check source date, geographic coverage, license and methodology. Community content may provide context but should not be the sole basis for high-consequence claims.

## Uncertainty
Name the uncertainty that matters: missing data, low resolution, mixed pixels, clouds, seasonal effects, uncertain location/date, unknown sampling depth, uncalibrated model, platform transformation or ambiguous image. Avoid generic disclaimers that do not help the user.

## Contradictions
If user records and external sources disagree, show the discrepancy, dates and units. Do not silently choose one. Ask which source is authoritative only when the conflict blocks the requested conclusion.
