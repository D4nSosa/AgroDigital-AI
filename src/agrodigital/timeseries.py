"""Temporal Sentinel-2 NDVI summaries and polygon statistics.

Inputs are already-derived, aligned NDVI GeoTIFF scenes. This module does not
fetch satellite data or infer that NDVI is a direct crop-health/yield measure.
"""
from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from .paths import resolve_work_path


class TimeSeriesError(ValueError):
    """Raised for invalid temporal raster inputs."""


def summarize_sentinel2_timeseries(scenes, aoi_geojson: dict, *,
                                   output_csv: str = "sentinel2_timeseries.csv",
                                   composite_path: str = "sentinel2_ndvi_median_composite.tif") -> dict:
    """Calculate per-scene polygon statistics and a per-pixel temporal median composite.

    Each scene is a mapping with ISO ``date`` and a path to a single-band NDVI
    GeoTIFF. All rasters must share an identical grid and CRS. AOI is RFC 7946
    GeoJSON geometry or Feature/FeatureCollection.
    """
    try:
        import numpy as np
        import rasterio
        from rasterio.features import geometry_mask
        from rasterio.warp import transform_geom
    except ImportError as exc:
        raise RuntimeError("Sentinel-2 time series requires numpy and rasterio.") from exc

    if not isinstance(scenes, (list, tuple)) or len(scenes) < 2:
        raise TimeSeriesError("At least two scenes are required for temporal analysis.")
    if not isinstance(aoi_geojson, dict):
        raise TimeSeriesError("aoi_geojson must be a GeoJSON object.")
    if aoi_geojson.get("type") == "FeatureCollection":
        geometries = [f.get("geometry") for f in aoi_geojson.get("features", []) if f.get("geometry")]
    elif aoi_geojson.get("type") == "Feature":
        geometries = [aoi_geojson.get("geometry")]
    else:
        geometries = [aoi_geojson]
    if not geometries:
        raise TimeSeriesError("AOI contains no geometry.")

    ordered = []
    for scene in scenes:
        if not isinstance(scene, dict) or not scene.get("date") or not scene.get("path"):
            raise TimeSeriesError("Each scene needs date and path fields.")
        try:
            scene_date = date.fromisoformat(str(scene["date"])[:10])
        except ValueError as exc:
            raise TimeSeriesError("Scene dates must be ISO dates.") from exc
        ordered.append((scene_date, resolve_work_path(scene["path"])))
    ordered.sort(key=lambda item: item[0])
    if len({day for day, _ in ordered}) != len(ordered):
        raise TimeSeriesError("Scene dates must be unique.")

    arrays = []
    rows = []
    reference_profile = None
    inside_mask = None
    for scene_date, scene_path in ordered:
        with rasterio.open(scene_path) as src:
            if src.count != 1:
                raise TimeSeriesError("Each NDVI scene must contain exactly one band.")
            if reference_profile is None:
                reference_profile = src.profile.copy()
                transformed = geometries
                if src.crs is None:
                    raise TimeSeriesError("Scene raster must declare a CRS.")
                if src.crs.to_epsg() != 4326:
                    transformed = [transform_geom("EPSG:4326", src.crs, geom) for geom in geometries]
                inside_mask = geometry_mask(transformed, out_shape=(src.height, src.width),
                                            transform=src.transform, invert=True)
            else:
                if (src.width, src.height, src.transform, src.crs) != (
                    reference_profile["width"], reference_profile["height"],
                    reference_profile["transform"], reference_profile["crs"]
                ):
                    raise TimeSeriesError("All scenes must have identical dimensions, transform and CRS.")
            band = src.read(1, masked=True).astype("float64")
            valid = (~np.ma.getmaskarray(band)) & inside_mask & np.isfinite(band.filled(np.nan))
            values = band.data[valid]
            if values.size:
                stats = {"mean": float(np.mean(values)), "median": float(np.median(values)),
                         "p10": float(np.percentile(values, 10)), "p90": float(np.percentile(values, 90))}
            else:
                stats = {key: None for key in ("mean", "median", "p10", "p90")}
            rows.append({"date": scene_date.isoformat(), "source_path": str(scene_path),
                         "valid_pixels": int(values.size), "aoi_pixels": int(inside_mask.sum()), **stats})
            scene_array = np.where(valid, band.data, np.nan)
            arrays.append(scene_array)

    stack = np.stack(arrays, axis=0)
    with np.errstate(all="ignore"):
        composite = np.nanmedian(stack, axis=0)
    composite_nodata = -9999.0
    composite = np.where(np.isfinite(composite), composite, composite_nodata).astype("float32")
    composite_output = resolve_work_path(composite_path, create_parent=True)
    profile = reference_profile.copy()
    profile.update(driver="GTiff", count=1, dtype="float32", nodata=composite_nodata,
                   compress="deflate", predictor=3)
    with rasterio.open(composite_output, "w", **profile) as dst:
        dst.write(composite, 1)
        dst.set_band_description(1, "Temporal median NDVI composite")
        dst.update_tags(method="per-pixel temporal median", scenes_count=str(len(ordered)),
                        software="AgroDigital-AI", statistic="median")

    csv_output = resolve_work_path(output_csv, create_parent=True)
    fields = ["date", "source_path", "valid_pixels", "aoi_pixels", "mean", "median", "p10", "p90"]
    with csv_output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    return {"status": "derived", "classification": "DERIVADO — estadísticas de NDVI por polígono",
            "scene_count": len(rows), "statistics_csv": str(csv_output),
            "temporal_median_composite": str(composite_output), "scenes": rows,
            "method": "per-scene AOI pixel statistics; per-pixel temporal median composite",
            "limitations": ["Input rasters must already be processed NDVI with consistent scaling and masks.",
                            "All scenes must share an identical grid and CRS.",
                            "NDVI is a spectral index, not direct yield, biomass, moisture or plant-health measurement.",
                            "Cloud/shadow quality depends on the upstream scene masks."]}
