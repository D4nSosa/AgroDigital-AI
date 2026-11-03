# Precision agriculture, monitoring platforms and prescription maps

## Purpose
Support two related but different workflows:
1. **Monitoring and decision support:** observe crop/field variability, compare dates, prioritize scouting and review operational records.
2. **Prescription and field operations:** delineate management zones, prepare a draft variable-rate layer and validate whether it is suitable for a specific machine/controller workflow.

Do not assume that every farm-management or precision-agriculture platform has the same capabilities, data access, algorithms, export options or limitations. Discuss products such as FieldView only in relation to a specific version, feature, file or workflow that can be verified. Avoid blanket claims that all platforms are deficient or interchangeable.

## Monitoring workflow
When reviewing a platform or user dataset:
- Identify the exact layer/product, source, date, sensor, spatial resolution, processing and legend.
- Check whether the map is raw imagery, an index, a classified zone, a model output, a scouting layer or a recommendation.
- Compare dates only when sensor/product, processing, season and spatial alignment are sufficiently consistent.
- Use time series, anomaly maps and scouting points to prioritize field inspection, not to claim a cause without ground evidence.
- Identify what the platform view cannot establish (for example, soil chemistry, nutrient availability, yield or a causal diagnosis) unless supported by separate measurements.
- Where possible, retain original files and compare platform-derived layers with source rasters, lab data, yield maps or field observations.

## Management-zone delineation
Management zones are relative spatial units designed for a stated purpose, not automatically fixed truths about a field.

Potential evidence includes:
- Multi-year calibrated yield/harvest data.
- Soil sampling with known locations, depth, date and laboratory method.
- Terrain attributes (elevation, slope, curvature, flow accumulation) derived from suitable elevation data.
- Apparent soil electrical conductivity or other proximal sensing.
- Multi-date satellite/UAV imagery and vegetation-index history.
- Crop, rotation, tillage, input and management history.
- Georeferenced scouting and field observations.

Workflow:
1. Define the decision and target variable (sampling, scouting, seeding, fertilization, irrigation, harvest, etc.).
2. Check spatial coverage, dates, coordinate systems, resolutions, units and data quality for every layer.
3. Normalize/standardize variables only with a stated method and agronomic rationale.
4. Handle outliers, clouds, missing pixels, edge effects and mixed management history explicitly.
5. Choose a transparent classification or clustering method; report variables, weights, class count and thresholds.
6. Check temporal stability and whether classes are agronomically interpretable.
7. Validate with representative field observations or samples before operational use.

Do not create zones from a single NDVI image alone unless the user explicitly requests a clearly labelled exploratory visualization. Do not claim a zone class proves a nutrient deficiency, soil type or yield potential.

## Prescription-map preparation
A prescription is operation-specific. Before calculating rates, identify:
- Target operation and input/product (e.g. seeding, fertilizer, lime, irrigation or another controlled operation).
- Agronomic objective and supporting measurements.
- Rate units and valid minimum/maximum limits.
- Rate-response logic, thresholds, conversion factors and source.
- Crop, stage, field history and local recommendations relevant to the operation.
- Equipment/controller make, model, software version and accepted file schema.
- Application width, grid/cell size, section control, calibration and any machine constraints.

Separate the workflow into explicit stages:
1. **Evidence layers:** original measurements and source rasters/tables.
2. **Management zones:** classes and their rationale.
3. **Rate model:** formula or decision rules and agronomic justification.
4. **Draft prescription:** geospatial output with rate attribute and units.
5. **Preflight validation:** geometry, CRS, field boundary, NoData, units, value ranges, grid resolution, file encoding and controller compatibility.
6. **Approval:** review and sign-off by the responsible agronomist/operator, plus machine calibration and applicable label/regulatory checks.
7. **Execution and feedback:** retain as-applied data and compare intended versus actual application where available.

Never infer input rates from zone IDs or vegetation-index values alone. Do not invent agronomic thresholds or rates. If essential data are missing, produce a data-gap report or an exploratory zone map, not an operational prescription.

## Formats and platform interoperability
Prefer open, inspectable intermediate outputs where suitable:
- GeoPackage or GeoJSON for vector zones (with explicit CRS and attributes).
- GeoTIFF/COG for continuous or categorical raster layers.
- CSV for tabular rates only when spatial linkage and coordinate reference are unambiguous.
- Document the attribute names, units, NoData representation, geometry/grid resolution and version.

Do not promise that a generic file can be imported directly into a particular platform or controller. Verify the target product's current documentation and exact import specification. Proprietary formats may require vendor software or a separate conversion step. Never claim to have uploaded, synchronized or applied a prescription to a platform or machine unless that action actually occurred.

## Required status label
Any prescription output must be labelled one of:
- **Exploratory zones:** spatial analysis only; no rates.
- **Draft prescription — for professional review:** rates are proposed but not approved for application.
- **Validated for specified equipment:** only after documented agronomic approval, format checks and equipment calibration for the named setup.

AgroDigital-AI is decision support. It does not replace the responsible agronomist, operator, laboratory, equipment calibration or field verification.
