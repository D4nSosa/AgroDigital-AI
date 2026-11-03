"""Explicit Sentinel-2 L2A NDVI processing from aligned band GeoTIFFs."""
from __future__ import annotations

from pathlib import Path


class Sentinel2Error(ValueError):
    """Raised for invalid Sentinel-2 processing inputs."""


DEFAULT_SCL_EXCLUDED = (0, 1, 3, 8, 9, 10, 11)


def calculate_sentinel2_ndvi(red_path: str | Path, nir_path: str | Path,
                             output_path: str | Path, *, scale_factor: float,
                             red_offset: float = 0.0, nir_offset: float = 0.0,
                             scl_path: str | Path | None = None,
                             excluded_scl_classes=DEFAULT_SCL_EXCLUDED) -> dict:
    """Calculate NDVI from Sentinel-2 L2A red/NIR GeoTIFFs.

    Inputs must already be on the same pixel grid and CRS. Reflectance is
    computed as DN / scale_factor + band_offset. The scale factor and offsets
    are explicit because product encoding and processing baseline can differ.
    If supplied, the SCL raster must share the exact grid; classes listed in
    excluded_scl_classes are masked. No atmospheric correction or resampling
    is performed here.
    """
    try:
        import numpy as np
        import rasterio
    except ImportError as exc:
        raise RuntimeError("Sentinel-2 processing requires: pip install 'agrodigital-ai[raster]'") from exc

    if not np.isfinite(scale_factor) or scale_factor <= 0:
        raise Sentinel2Error("scale_factor must be a finite positive number.")
    if not np.isfinite(red_offset) or not np.isfinite(nir_offset):
        raise Sentinel2Error("Band offsets must be finite numbers.")
    excluded = tuple(int(value) for value in excluded_scl_classes)

    with rasterio.open(red_path) as red, rasterio.open(nir_path) as nir:
        if red.count < 1 or nir.count < 1:
            raise Sentinel2Error("Red and NIR rasters must contain at least one band.")
        if (red.width, red.height, red.transform, red.crs) != (nir.width, nir.height, nir.transform, nir.crs):
            raise Sentinel2Error("Red and NIR rasters are not aligned; align them explicitly before processing.")
        red_data = red.read(1, masked=True).astype("float32")
        nir_data = nir.read(1, masked=True).astype("float32")
        valid = (~np.ma.getmaskarray(red_data)) & (~np.ma.getmaskarray(nir_data))
        red_reflectance = red_data.filled(0) / scale_factor + red_offset
        nir_reflectance = nir_data.filled(0) / scale_factor + nir_offset

        if scl_path is not None:
            with rasterio.open(scl_path) as scl:
                if (red.width, red.height, red.transform, red.crs) != (scl.width, scl.height, scl.transform, scl.crs):
                    raise Sentinel2Error("SCL raster is not aligned with red/NIR inputs.")
                scl_data = scl.read(1, masked=True)
                scl_values = scl_data.filled(-1)
                valid &= ~np.ma.getmaskarray(scl_data)
                valid &= ~np.isin(scl_values, excluded)

        denominator = nir_reflectance + red_reflectance
        valid &= np.isfinite(denominator) & (denominator != 0)
        output = np.full((red.height, red.width), -9999.0, dtype="float32")
        np.divide(nir_reflectance - red_reflectance, denominator,
                  out=output, where=valid)
        profile = red.profile.copy()
        profile.update(driver="GTiff", count=1, dtype="float32", nodata=-9999.0,
                       compress="deflate", predictor=3)
        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(output, 1)
            dst.set_band_description(1, "Sentinel-2 L2A NDVI")
            dst.update_tags(
                software="AgroDigital-AI", product="Sentinel-2 L2A",
                formula="(NIR-RED)/(NIR+RED)", red_source=str(red_path),
                nir_source=str(nir_path), scl_source=str(scl_path) if scl_path else "not supplied",
                scale_factor=str(scale_factor), red_offset=str(red_offset),
                nir_offset=str(nir_offset), excluded_scl_classes=",".join(map(str, excluded)),
                cloud_mask="SCL class exclusion" if scl_path else "not applied",
                processing_note="Inputs assumed preprocessed L2A reflectance DN; no atmospheric correction or resampling performed."
            )
    return {"output": str(output_path), "index": "NDVI", "formula": "(NIR-RED)/(NIR+RED)",
            "scale_factor": scale_factor, "red_offset": red_offset, "nir_offset": nir_offset,
            "scl_applied": scl_path is not None, "excluded_scl_classes": list(excluded),
            "nodata": -9999.0, "crs": rasterio.open(output_path).crs.to_string() if rasterio.open(output_path).crs else None}
