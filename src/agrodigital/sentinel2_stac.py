"""End-to-end Sentinel-2 processing from a public STAC Item."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from .download import download_asset
from .sentinel2 import calculate_sentinel2_ndvi
from .stac import DEFAULT_STAC_URL, get_stac_item


class Sentinel2STACError(ValueError):
    """Raised when a STAC Item cannot support the requested Sentinel-2 workflow."""


def _asset_href(item: dict, key: str) -> str:
    asset = (item.get("assets") or {}).get(key)
    if not isinstance(asset, dict) or not asset.get("href"):
        raise Sentinel2STACError(f"Required STAC asset '{key}' is not available.")
    href = asset["href"]
    parsed = urlparse(href)
    if parsed.scheme != "https" or not parsed.netloc:
        raise Sentinel2STACError(f"Asset '{key}' does not have a public HTTPS URL.")
    return href


def _reflectance_parameters(item: dict, asset_key: str) -> dict:
    asset = item["assets"][asset_key]
    raster_bands = asset.get("raster:bands") or []
    band = raster_bands[0] if raster_bands else {}
    scale = band.get("scale", 0.0001)
    try:
        scale = float(scale)
    except (TypeError, ValueError) as exc:
        raise Sentinel2STACError(f"Invalid raster:bands scale for '{asset_key}'.") from exc
    if scale <= 0:
        raise Sentinel2STACError(f"Non-positive raster:bands scale for '{asset_key}'.")
    properties = item.get("properties") or {}
    if "earthsearch:boa_offset_applied" in properties:
        offset = 0.0 if properties["earthsearch:boa_offset_applied"] is True else -1000.0 * scale
        rule = "earthsearch:boa_offset_applied"
    elif properties.get("s2:processing_baseline") is not None:
        try:
            baseline = float(properties["s2:processing_baseline"])
            offset = -1000.0 * scale if baseline >= 4.0 else 0.0
            rule = "s2:processing_baseline"
        except (TypeError, ValueError):
            offset = float(band.get("offset", 0.0) or 0.0)
            rule = "raster:bands.offset fallback; baseline unparseable"
    else:
        offset = float(band.get("offset", 0.0) or 0.0)
        rule = "raster:bands.offset or zero"
    return {"scale_factor": 1.0 / scale, "offset": offset,
            "source_scale": scale, "source_offset": band.get("offset"),
            "offset_rule": rule}


def process_sentinel2_stac_item(
    item_id: str, output_dir: str | Path, *, output_path: str | Path | None = None,
    collection: str = "sentinel-2-l2a", endpoint: str = DEFAULT_STAC_URL,
    max_bytes_per_asset: int = 2_000_000_000, timeout: int = 60,
    use_scl: bool = True, overwrite: bool = False,
) -> dict:
    """Download red/NIR/(optional SCL) assets from one STAC Item and calculate NDVI.

    The scene is processed at its native grid. This function does not clip to an AOI,
    resample, perform atmospheric correction or guarantee cloud-free pixels.
    """
    item = get_stac_item(item_id, collection=collection, endpoint=endpoint, timeout=timeout)
    assets = item.get("assets") or {}
    red_key = "red" if "red" in assets else "B04" if "B04" in assets else None
    nir_key = "nir" if "nir" in assets else "B08" if "B08" in assets else None
    scl_key = "scl" if "scl" in assets else "SCL" if "SCL" in assets else None
    if not red_key or not nir_key:
        raise Sentinel2STACError("The selected STAC Item must contain red and nir (or B04/B08) assets.")
    if use_scl and not scl_key:
        raise Sentinel2STACError("SCL masking was requested but the STAC Item has no SCL asset.")

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    safe_id = re.sub(r"[^A-Za-z0-9._-]+", "_", str(item.get("id", item_id)))
    downloaded = {}
    for logical_name, key in (("red", red_key), ("nir", nir_key), ("scl", scl_key if use_scl else None)):
        if key is None:
            continue
        asset_path = destination / f"{safe_id}_{logical_name}.tif"
        downloaded[logical_name] = download_asset(
            _asset_href(item, key), asset_path, max_bytes=max_bytes_per_asset,
            timeout=timeout, overwrite=overwrite,
        )

    red_params = _reflectance_parameters(item, red_key)
    nir_params = _reflectance_parameters(item, nir_key)
    ndvi_path = Path(output_path) if output_path else destination / f"{safe_id}_ndvi.tif"
    processing = calculate_sentinel2_ndvi(
        downloaded["red"]["path"], downloaded["nir"]["path"], ndvi_path,
        scale_factor=red_params["scale_factor"],
        red_offset=red_params["offset"], nir_offset=nir_params["offset"],
        scl_path=downloaded["scl"]["path"] if "scl" in downloaded else None,
    )
    license_links = [link.get("href") for link in item.get("links", [])
                     if link.get("rel") == "license" and link.get("href")]
    properties = item.get("properties") or {}
    return {
        "status": "processed",
        "item": {"id": item.get("id"), "collection": item.get("collection"),
                 "datetime": properties.get("datetime"),
                 "cloud_cover_percent": properties.get("eo:cloud_cover"),
                 "bbox": item.get("bbox"), "license_urls": license_links},
        "assets_downloaded": downloaded,
        "reflectance_parameters": {"red": red_params, "nir": nir_params},
        "processing": processing,
        "provenance": {
            "catalog": endpoint, "item_id": item.get("id"),
            "collection": item.get("collection"), "asset_keys": {
                "red": red_key, "nir": nir_key, "scl": scl_key if use_scl else None},
            "acquisition_datetime": properties.get("datetime"),
            "cloud_cover_percent": properties.get("eo:cloud_cover"),
            "method": "NDVI = (NIR reflectance - red reflectance) / (NIR reflectance + red reflectance)",
            "reflectance_rule": "reflectance = DN * STAC raster:bands scale + metadata-derived offset",
            "limitations": [
                "Native scene grid; no AOI clipping or resampling.",
                "SCL class exclusion is not a guarantee of cloud-free pixels.",
                "No atmospheric correction is performed by this workflow.",
                "Verify product metadata and license before operational use.",
            ],
        },
    }
