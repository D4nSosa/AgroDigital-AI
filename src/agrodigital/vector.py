"""Optional vector reprojection and topology checks."""
from __future__ import annotations

import json
from pathlib import Path


class VectorError(ValueError):
    """Raised for invalid vector data or coordinate transformations."""


def reproject_geojson(input_path: str | Path, output_path: str | Path,
                      source_crs: str, target_crs: str) -> dict:
    """Reproject GeoJSON coordinates with pyproj; source CRS must be explicit."""
    try:
        from pyproj import Transformer
    except ImportError as exc:
        raise RuntimeError("Vector reprojection requires: pip install 'agrodigital-ai[geo]'") from exc
    if not source_crs or not target_crs:
        raise VectorError("Both source_crs and target_crs must be explicit.")
    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))

    def position(coord):
        if not isinstance(coord, (list, tuple)) or len(coord) < 2:
            raise VectorError("Invalid coordinate position.")
        x, y = transformer.transform(coord[0], coord[1])
        return [x, y, *coord[2:]]

    def coordinates(value):
        if isinstance(value, (list, tuple)) and len(value) >= 2 and all(isinstance(v, (int, float)) for v in value[:2]):
            return position(value)
        if isinstance(value, (list, tuple)):
            return [coordinates(item) for item in value]
        raise VectorError("Invalid GeoJSON coordinates.")

    def geometry(g):
        if g is None:
            return None
        if g.get("type") == "GeometryCollection":
            return {**g, "geometries": [geometry(item) for item in g.get("geometries", [])]}
        return {**g, "coordinates": coordinates(g.get("coordinates"))}

    if data.get("type") == "FeatureCollection":
        data["features"] = [{**f, "geometry": geometry(f.get("geometry"))} for f in data.get("features", [])]
    elif data.get("type") == "Feature":
        data["geometry"] = geometry(data.get("geometry"))
    else:
        data = geometry(data)
    Path(output_path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"output": str(output_path), "source_crs": source_crs,
            "target_crs": target_crs, "axis_order": "x,y (always_xy)"}


def validate_topology(geojson_path: str | Path) -> dict:
    """Validate geometry topology with Shapely; does not repair geometries."""
    try:
        from shapely.geometry import shape
    except ImportError as exc:
        raise RuntimeError("Topology validation requires: pip install 'agrodigital-ai[geo]'") from exc
    data = json.loads(Path(geojson_path).read_text(encoding="utf-8"))
    if data.get("type") == "FeatureCollection":
        features = data.get("features", [])
    elif data.get("type") == "Feature":
        features = [data]
    else:
        features = [{"geometry": data}]
    results = []
    for index, feature in enumerate(features):
        geom_data = feature.get("geometry")
        if geom_data is None:
            results.append({"feature": index, "valid": True, "empty_geometry": True})
            continue
        geom = shape(geom_data)
        results.append({"feature": index, "valid": bool(geom.is_valid),
                        "geometry_type": geom.geom_type, "empty": bool(geom.is_empty),
                        "reason": None if geom.is_valid else "Invalid geometry; inspect before use."})
    return {"valid": all(item["valid"] for item in results), "feature_count": len(results),
            "features": results, "note": "Validation only; no automatic repair or reprojection."}
