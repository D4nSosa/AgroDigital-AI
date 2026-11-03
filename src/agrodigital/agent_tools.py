"""Provider-neutral functions exposed to AI agents and other automation clients."""
from __future__ import annotations

from .core import inspect_python_capabilities
from .geo import GeoJSONError, validate_geojson
from .sentinel2_stac import process_sentinel2_stac_item
from .stac import DEFAULT_STAC_URL, search_stac
from .weather import growing_degree_days, rainfall_total


def plan_analysis(objective: str, *, aoi_geojson: dict | None = None,
                  bbox: list[float] | None = None, date_range: str | None = None,
                  crop_or_species: str | None = None,
                  available_inputs: list[str] | None = None) -> dict:
    """Build an evidence-aware plan; this function does not invent analysis results."""
    if not objective or not objective.strip():
        raise ValueError("objective is required.")
    if aoi_geojson is not None and bbox is not None:
        raise ValueError("Provide aoi_geojson or bbox, not both.")
    aoi_status = "provided"
    if aoi_geojson is not None:
        try:
            aoi_validation = validate_geojson(aoi_geojson)
        except GeoJSONError as exc:
            return {"status": "needs_input", "objective": objective,
                    "aoi_status": "invalid", "aoi_validation_error": str(exc),
                    "missing_or_uncertain": ["A valid WGS84 GeoJSON AOI is required before spatial analysis."]}
        if not aoi_validation.get("valid", False):
            return {"status": "needs_input", "objective": objective,
                    "aoi_validation": aoi_validation,
                    "missing_or_uncertain": ["A valid AOI geometry is required before spatial analysis."]}
    elif bbox is not None:
        if len(bbox) != 4 or not (-180 <= bbox[0] < bbox[2] <= 180 and -90 <= bbox[1] < bbox[3] <= 90):
            raise ValueError("bbox must be [west,south,east,north] in EPSG:4326.")
    else:
        aoi_status = "missing"

    inputs = [str(value) for value in (available_inputs or [])]
    missing = []
    if aoi_status == "missing":
        missing.append("A georeferenced AOI (GeoJSON/bbox) or a location that can be resolved.")
    if not date_range:
        missing.append("A date or analysis period if the task depends on temporal data.")
    if not crop_or_species:
        missing.append("Crop/species or production system when the requested decision depends on it.")
    if not inputs:
        missing.append("Available evidence: image, raster, soil analysis, field observations, or weather data.")

    return {
        "status": "plan_only",
        "objective": objective.strip(),
        "aoi_status": aoi_status,
        "aoi_type": "GeoJSON" if aoi_geojson is not None else "bbox" if bbox is not None else None,
        "date_range": date_range,
        "crop_or_species": crop_or_species,
        "available_inputs": inputs,
        "workflow": [
            "Inspect each supplied file and identify its type, metadata, date, units and spatial reference.",
            "Separate visual observations from measurements and model-derived indicators.",
            "Resolve the AOI and period before querying external datasets.",
            "Select only datasets with verified coverage, access terms and relevant resolution.",
            "Run supported calculations and validate outputs before drawing operational conclusions.",
            "Report evidence, assumptions, uncertainty, missing measurements and reproducible outputs.",
        ],
        "missing_or_uncertain": missing,
        "guardrails": [
            "An ordinary photograph cannot establish soil chemistry, nutrient status or yield.",
            "A vegetation index is not a direct measurement of yield, species or plant health.",
            "Do not issue high-consequence input or machinery prescriptions without local measurements and qualified review.",
        ],
        "execution": "No geospatial processing or external data retrieval was performed by this planning tool.",
    }


def get_capabilities() -> dict:
    return inspect_python_capabilities(
        modules=("numpy", "shapely", "pyproj", "rasterio", "mcp")
    ).to_dict()


def search_satellite_scenes(bbox: list[float], datetime_range: str, *,
                            collections: list[str] | None = None,
                            cloud_cover_max: float | None = None,
                            max_items: int = 10,
                            endpoint: str = DEFAULT_STAC_URL) -> dict:
    return search_stac(
        bbox=bbox, datetime=datetime_range,
        collections=collections or ["sentinel-2-l2a"],
        cloud_cover_max=cloud_cover_max, max_items=max_items, endpoint=endpoint,
    )


def process_sentinel2_scene(item_id: str, output_dir: str, *,
                            output_path: str | None = None,
                            collection: str = "sentinel-2-l2a",
                            endpoint: str = DEFAULT_STAC_URL,
                            max_bytes_per_asset: int = 2_000_000_000,
                            use_scl: bool = True, overwrite: bool = False) -> dict:
    return process_sentinel2_stac_item(
        item_id, output_dir, output_path=output_path, collection=collection,
        endpoint=endpoint, max_bytes_per_asset=max_bytes_per_asset,
        use_scl=use_scl, overwrite=overwrite,
    )


def calculate_gdd(tmin_c: float, tmax_c: float, base_c: float,
                  upper_c: float | None = None) -> dict:
    return {"gdd_degree_days": growing_degree_days(tmin_c, tmax_c, base_c, upper_c=upper_c),
            "unit": "°C·day", "method": "daily mean temperature"}


def calculate_rainfall(values_mm: list[float]) -> dict:
    return {"rainfall_total_mm": rainfall_total(values_mm), "unit": "mm",
            "observations_count": len(values_mm)}
