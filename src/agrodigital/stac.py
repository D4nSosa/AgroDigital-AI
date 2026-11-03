"""Credential-free STAC search and item retrieval for public satellite catalogs."""
from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlparse
from urllib.request import Request, urlopen

DEFAULT_STAC_URL = "https://earth-search.aws.element84.com/v1"


class STACError(RuntimeError):
    """Raised when a STAC catalog cannot be queried or returns invalid data."""


def _read_json(url: str, *, data: bytes | None = None, method: str = "GET",
               timeout: int = 45) -> dict:
    request = Request(
        url, data=data, method=method,
        headers={"Accept": "application/geo+json, application/json",
                 "Content-Type": "application/json",
                 "User-Agent": "AgroDigital-AI/0.4"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise STACError(f"STAC request failed: {exc}") from exc
    if not isinstance(result, dict):
        raise STACError("STAC response must be a JSON object.")
    return result


def search_stac(*, bbox=None, intersects=None, datetime=None,
                collections=("sentinel-2-l2a",), max_items=20,
                cloud_cover_max=None, endpoint=DEFAULT_STAC_URL, timeout=45) -> dict:
    """Search a public STAC API. bbox uses EPSG:4326; provide bbox or intersects."""
    if (bbox is None) == (intersects is None):
        raise ValueError("Provide exactly one of bbox or intersects.")
    if not isinstance(max_items, int) or not 1 <= max_items <= 500:
        raise ValueError("max_items must be between 1 and 500.")
    parsed_endpoint = urlparse(endpoint)
    if parsed_endpoint.scheme != "https" or not parsed_endpoint.netloc:
        raise ValueError("STAC endpoint must be an HTTPS URL.")
    payload = {"limit": min(max_items, 100), "collections": list(collections)}
    if bbox is not None:
        if len(bbox) != 4 or not (-180 <= bbox[0] <= 180 and -180 <= bbox[2] <= 180
                                  and -90 <= bbox[1] <= 90 and -90 <= bbox[3] <= 90
                                  and bbox[0] < bbox[2] and bbox[1] < bbox[3]):
            raise ValueError("bbox must be [west,south,east,north] in valid EPSG:4326 ranges.")
        payload["bbox"] = list(bbox)
    else:
        if not isinstance(intersects, dict):
            raise ValueError("intersects must be a GeoJSON geometry object.")
        payload["intersects"] = intersects
    if datetime:
        payload["datetime"] = datetime
    if cloud_cover_max is not None:
        if not 0 <= cloud_cover_max <= 100:
            raise ValueError("cloud_cover_max must be between 0 and 100.")
        payload["query"] = {"eo:cloud_cover": {"lte": cloud_cover_max}}

    query_summary = {key: value for key, value in payload.items() if key != "limit"}
    features = []
    url = endpoint.rstrip("/") + "/search"
    method = "POST"
    while url and len(features) < max_items:
        body = json.dumps(payload).encode("utf-8") if method == "POST" else None
        result = _read_json(url, data=body, method=method, timeout=timeout)
        page_features = result.get("features")
        if not isinstance(page_features, list):
            raise STACError("STAC response is missing a features array.")
        features.extend(page_features)
        next_link = next((link for link in result.get("links", [])
                          if link.get("rel") == "next" and link.get("href")), None)
        if not next_link:
            break
        next_url = urljoin(url, next_link["href"])
        next_parsed = urlparse(next_url)
        if next_parsed.scheme != "https" or next_parsed.netloc != parsed_endpoint.netloc:
            raise STACError("Refusing pagination outside the configured HTTPS STAC host.")
        url = next_url
        method = next_link.get("method", "GET").upper()
        if method not in {"GET", "POST"}:
            raise STACError("Unsupported STAC pagination method.")
        payload = next_link.get("body", payload) if method == "POST" else {}

    items = []
    for feature in features[:max_items]:
        properties = feature.get("properties") or {}
        assets = feature.get("assets") or {}
        items.append({
            "id": feature.get("id"),
            "collection": feature.get("collection"),
            "datetime": properties.get("datetime") or properties.get("start_datetime"),
            "cloud_cover_percent": properties.get("eo:cloud_cover"),
            "bbox": feature.get("bbox"),
            "geometry": feature.get("geometry"),
            "assets": {name: asset.get("href") for name, asset in assets.items() if asset.get("href")},
            "asset_details": assets,
        })
    return {
        "endpoint": endpoint, "query": query_summary, "returned_items": len(items),
        "items": items,
        "note": "Catalog metadata only. Assets have not been downloaded or processed.",
    }


def get_stac_item(item_id: str, *, collection: str = "sentinel-2-l2a",
                  endpoint: str = DEFAULT_STAC_URL, timeout: int = 45) -> dict:
    """Retrieve one complete STAC Item, including asset and raster-band metadata."""
    parsed = urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("STAC endpoint must be an HTTPS URL.")
    if not item_id or not collection:
        raise ValueError("item_id and collection are required.")
    url = (endpoint.rstrip("/") + "/collections/" + quote(collection, safe="") +
           "/items/" + quote(item_id, safe=""))
    item = _read_json(url, timeout=timeout)
    if not item.get("id") or not isinstance(item.get("assets"), dict):
        raise STACError("STAC Item response is missing id or assets.")
    return item
