"""Optional Rasterio workflows for GeoTIFF inspection and processing.

All raster operations are explicit about band numbers (1-based), CRS and nodata.
"""
from __future__ import annotations

import json
from pathlib import Path


class RasterError(ValueError):
    """Raised for unsupported or invalid raster operations."""


def _rasterio():
    try:
        import rasterio
        return rasterio
    except ImportError as exc:
        raise RuntimeError("Raster operations require optional dependencies: pip install 'agrodigital-ai[raster]'") from exc


def inspect_raster(path: str | Path) -> dict:
    """Return raster metadata without loading the full pixel array."""
    rasterio = _rasterio()
    with rasterio.open(path) as src:
        bounds = src.bounds
        return {
            "path": str(path), "driver": src.driver, "width": src.width,
            "height": src.height, "band_count": src.count, "dtypes": list(src.dtypes),
            "crs": src.crs.to_string() if src.crs else None,
            "transform": list(src.transform), "bounds": [bounds.left, bounds.bottom, bounds.right, bounds.top],
            "resolution": [abs(src.transform.a), abs(src.transform.e)],
            "nodata": src.nodata, "pixel_count": src.width * src.height,
            "file_size_bytes": Path(path).stat().st_size,
        }


def calculate_normalized_difference(input_path: str | Path, output_path: str | Path,
                                    band_a: int, band_b: int, *, label: str = "normalized_difference") -> dict:
    """Write (band_a-band_b)/(band_a+band_b) as a float32 GeoTIFF."""
    import numpy as np
    rasterio = _rasterio()
    if band_a < 1 or band_b < 1 or band_a == band_b:
        raise RasterError("Band numbers must be distinct positive 1-based indices.")
    with rasterio.open(input_path) as src:
        if max(band_a, band_b) > src.count:
            raise RasterError(f"Requested band exceeds raster band count ({src.count}).")
        a = src.read(band_a, masked=True).astype("float32")
        b = src.read(band_b, masked=True).astype("float32")
        denominator = a + b
        valid = (~np.ma.getmaskarray(a)) & (~np.ma.getmaskarray(b)) & (denominator.filled(0) != 0)
        result = np.full((src.height, src.width), -9999.0, dtype="float32")
        np.divide((a - b).filled(0), denominator.filled(1), out=result, where=valid)
        profile = src.profile.copy()
        profile.update(driver="GTiff", count=1, dtype="float32", nodata=-9999.0,
                       compress="deflate", predictor=3)
        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(result, 1)
            dst.set_band_description(1, label)
            dst.update_tags(1, formula="(band_a-band_b)/(band_a+band_b)",
                            input_bands=f"{band_a},{band_b}", method="normalized difference",
                            source=str(input_path), software="AgroDigital-AI")
            dst.update_tags(AREA_OR_POINT="Area")
    return {"output": str(output_path), "formula": "(A-B)/(A+B)",
            "band_a": band_a, "band_b": band_b, "nodata": -9999.0,
            "crs": inspect_raster(output_path)["crs"]}


def clip_raster(input_path: str | Path, geojson_path: str | Path,
                output_path: str | Path, *, crop: bool = True) -> dict:
    """Mask a raster using GeoJSON features (RFC 7946 coordinates)."""
    rasterio = _rasterio()
    from rasterio.mask import mask
    from rasterio.warp import transform_geom
    data = json.loads(Path(geojson_path).read_text(encoding="utf-8"))
    if data.get("type") == "FeatureCollection":
        features = data.get("features", [])
    elif data.get("type") == "Feature":
        features = [data]
    else:
        features = [{"type": "Feature", "properties": {}, "geometry": data}]
    geometries = [f.get("geometry") for f in features if f.get("geometry")]
    if not geometries:
        raise RasterError("GeoJSON contains no usable geometries.")
    with rasterio.open(input_path) as src:
        if not src.crs:
            raise RasterError("Input raster has no CRS; clipping cannot safely transform coordinates.")
        if src.crs.to_epsg() != 4326:
            geometries = [transform_geom("EPSG:4326", src.crs, g) for g in geometries]
        output_nodata = src.nodata if src.nodata is not None else 0
        try:
            image, transform = mask(src, geometries, crop=crop, filled=True,
                                    nodata=output_nodata)
        except ValueError as exc:
            raise RasterError(f"AOI does not overlap raster or geometry is invalid: {exc}") from exc
        profile = src.profile.copy()
        profile.update(height=image.shape[1], width=image.shape[2], transform=transform,
                       nodata=output_nodata, compress="deflate")
        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(image)
            dst.update_tags(source=str(input_path), clip_geometry=str(geojson_path),
                            software="AgroDigital-AI")
    return {"output": str(output_path), "width": int(image.shape[2]),
            "height": int(image.shape[1]), "bands": int(image.shape[0]),
            "crs": inspect_raster(output_path)["crs"]}


def reproject_raster(input_path: str | Path, output_path: str | Path, target_crs: str) -> dict:
    """Reproject every band to an explicit target CRS using nearest-neighbour resampling."""
    rasterio = _rasterio()
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    with rasterio.open(input_path) as src:
        if not src.crs:
            raise RasterError("Input raster has no CRS; assign its real CRS before reprojection.")
        transform, width, height = calculate_default_transform(
            src.crs, target_crs, src.width, src.height, *src.bounds)
        profile = src.profile.copy()
        profile.update(crs=target_crs, transform=transform, width=width, height=height,
                       compress="deflate")
        with rasterio.open(output_path, "w", **profile) as dst:
            for index in range(1, src.count + 1):
                reproject(source=rasterio.band(src, index), destination=rasterio.band(dst, index),
                          src_transform=src.transform, src_crs=src.crs,
                          dst_transform=transform, dst_crs=target_crs,
                          resampling=Resampling.nearest)
            dst.update_tags(source=str(input_path), resampling="nearest",
                            target_crs=target_crs, software="AgroDigital-AI")
    return {"output": str(output_path), "target_crs": target_crs,
            "width": width, "height": height}
