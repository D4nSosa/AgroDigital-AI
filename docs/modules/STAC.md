# Public satellite catalog discovery

AgroDigital-AI includes a minimal STAC API client for catalog discovery. Its default endpoint is AWS Earth Search; the endpoint can be overridden with another HTTPS STAC API.

Example:
```bash
agrodigital stac-search --bbox -56 -29 -54 -27 \
  --datetime 2026-01-01T00:00:00Z/2026-02-01T00:00:00Z \
  --collections sentinel-2-l2a --max-items 20
```

Use `--intersects path/to/aoi.geojson` instead of `--bbox` for a polygon. The client returns item identifiers, collection, acquisition time, cloud-cover metadata, bounding boxes and asset references.

The search is metadata-only. No asset download, cloud masking, atmospheric correction, pixel processing, cache, retry queue or signed-URL refresh is implemented yet. Catalog metadata and licensing/availability can change; verify every item and asset before use. Never treat a catalog hit as a successfully downloaded scene.
