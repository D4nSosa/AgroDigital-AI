"""Credential-free STAC API search for public satellite catalogs."""
from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DEFAULT_STAC_URL = "https://earth-search.aws.element84.com/v1"


class STACError(RuntimeError):
    """Raised when a STAC catalog cannot be queried or returns invalid data."""


def search_stac(*, bbox=None, intersects=None, datetime=None,
                collections=("sentinel-2-l2a",), max_items=20,
                cloud_cover_max=None, endpoint=DEFAULT_STAC_URL, timeout=45) -> dict:
    """Search a public STAC API. No API key is requested or assumed.

    bbox is [west,south,east,north] in EPSG:4326. Use either bbox or
    intersects (GeoJSON geometry), not both. datetime follows STAC RFC3339
    interval syntax, e.g. 2026-01-01T00:00:00Z/2026-02-01T00:00:00Z.
    """
    if (bbox is None) == (intersects is None):
        raise ValueError("Provide exactly one of bbox or intersects.")
    if not isinstance(max_items, int) or not 1 <= max_items <= 500:
        raise ValueError("max_items must be between 1 and 500.")
    parsed = urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("STAC endpoint must be an HTTPS URL.")
    payload = {"limit": min(max_items, 100), "collections": list(collections)}
    if bbox is not None:
        if len(bbox) != 4 or not (-180 <= bbox[0] <= 180 and -180 <= bbox[2] <= 180
                                  and -90 <= bbox[1] <= 90 and -90 <= bbox[3] <= 90
                                  and bbox[0] < bbox[2] and bbox[1] < bbox[3]):
            raise ValueError("bbox must be [west,south,east,north] in valid EPSG:4326 ranges.")
        payload["bbox"] = list(bbox)
    else:
        payload["intersects"] = intersects
    if datetime:
        payload["datetime"] = datetime
    if cloud_cover_max is not None:
        if not 0 <= cloud_cover_max <= 100:
            raise ValueError("cloud_cover_max must be between 0 and 100.")
        payload["query"] = {"eo:cloud_cover": {"lte": cloud_cover_max}}

    features = []
    url = endpoint.rstrip("/") + "/search"
    method = "POST"
    while url and len(features) < max_items:
        body = json.dumps(payload).encode("utf-8") if method == "POST" else None
        request = Request(url, data=body, method=method,
                          headers={"Accept": "application/geo+json, application/json",
                                   "Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise STACError(f"STAC request failed: {exc}") from exc
        if not isinstance(result, dict) or not isinstance(result.get("features"), list):
            raise STACError("STAC response is missing a features array.")
        features.extend(result["features"])
        next_link = next((link for link in result.get("links", [])
                          if link.get("rel") == "next" and link.get("href")), None)
        if not next_link:
            break
        next_url = next_link["href"]
        if urlparse(next_url).scheme != "https":
            raise STACError("Refusing non-HTTPS pagination URL.")
        url = next_url
        method = next_link.get("method", "GET").upper()
        if method not in {"GET", "POST"}:
            raise STACError("Unsupported STAC pagination method.")
        payload = next_link.get("body", payload) if method == "POST" else {}

    items = []
    for feature in features[:max_items]:
        props = feature.get("properties") or {}
        items.append({
            "id": feature.get("id"), "collection": feature.get("collection"),
            "datetime": props.get("datetime") or props.get("start_datetime"),
            "cloud_cover_percent": props.get("eo:cloud_cover"),
            "bbox": feature.get("bbox"),
            "assets": {name: asset.get("href") for name, asset in (feature.get("assets") or {}).items()
                       if asset.get("href")},
        })
    return {"endpoint": endpoint, "query": {k: v for k, v in payload.items() if k != "limit"},
            "returned_items": len(items), "items": items,
            "note": "Catalog metadata only. Assets have not been downloaded or processed."}
