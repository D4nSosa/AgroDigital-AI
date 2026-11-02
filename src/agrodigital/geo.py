"""Small GeoJSON utilities using only the Python standard library."""
import json
from pathlib import Path

class GeoJSONError(ValueError):
    """Raised when a GeoJSON document is invalid or unsupported."""

def _walk_positions(value):
    if not isinstance(value, (list, tuple)):
        return
    if len(value) >= 2 and all(isinstance(v, (int, float)) for v in value[:2]):
        yield value
        return
    for child in value:
        yield from _walk_positions(child)

def _validate_geometry_positions(geometry):
    if not isinstance(geometry, dict):
        raise GeoJSONError("Geometry must be an object.")
    kind = geometry.get("type")
    if kind == "GeometryCollection":
        items = geometry.get("geometries", [])
        if not isinstance(items, list):
            raise GeoJSONError("GeometryCollection.geometries must be a list.")
        return sum(_validate_geometry_positions(g) for g in items)
    if kind not in {"Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"}:
        raise GeoJSONError(f"Unsupported geometry type: {kind!r}")
    coords = geometry.get("coordinates")
    if coords is None:
        raise GeoJSONError(f"{kind} geometry is missing coordinates.")
    positions = list(_walk_positions(coords))
    if not positions:
        raise GeoJSONError(f"{kind} geometry has no coordinate positions.")
    for position in positions:
        lon, lat = position[0], position[1]
        if not (-180 <= lon <= 180):
            raise GeoJSONError(f"Longitude outside [-180, 180]: {lon}")
        if not (-90 <= lat <= 90):
            raise GeoJSONError(f"Latitude outside [-90, 90]: {lat}")
    if kind == "Polygon":
        _check_polygon_rings(coords)
    elif kind == "MultiPolygon":
        for polygon in coords:
            _check_polygon_rings(polygon)
    return len(positions)

def _check_polygon_rings(rings):
    if not isinstance(rings, list) or not rings:
        raise GeoJSONError("Polygon must contain at least one linear ring.")
    for ring in rings:
        if not isinstance(ring, list) or len(ring) < 4:
            raise GeoJSONError("A linear ring must contain at least four positions.")
        if ring[0][:2] != ring[-1][:2]:
            raise GeoJSONError("Linear ring must be closed (first and last positions equal).")

def validate_geojson(data):
    """Check GeoJSON structure and WGS84 longitude/latitude ranges.

    This is not full topology validation and does not reproject coordinates.
    """
    if not isinstance(data, dict):
        raise GeoJSONError("The GeoJSON root must be an object.")
    kind = data.get("type")
    if kind == "FeatureCollection":
        features = data.get("features")
        if not isinstance(features, list):
            raise GeoJSONError("FeatureCollection.features must be a list.")
        geometries = []
        for feature in features:
            if not isinstance(feature, dict) or feature.get("type") != "Feature":
                raise GeoJSONError("Each FeatureCollection item must be a Feature object.")
            if feature.get("geometry") is not None:
                geometries.append(feature["geometry"])
    elif kind == "Feature":
        geometries = [data["geometry"]] if data.get("geometry") is not None else []
    elif kind in {"Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon", "GeometryCollection"}:
        geometries = [data]
    else:
        raise GeoJSONError(f"Unsupported GeoJSON type: {kind!r}")
    count = sum(_validate_geometry_positions(g) for g in geometries)
    return {"valid": True, "type": kind, "feature_count": len(data.get("features", [])) if kind == "FeatureCollection" else 1, "coordinate_count": count, "crs_assumption": "WGS84 longitude/latitude (RFC 7946)", "limitations": ["Structural validation only; not full topology validation.", "Coordinates are assumed to be WGS84 longitude/latitude.", "No area or distance calculation is performed."]}

def load_geojson(path):
    """Load and validate a GeoJSON file from disk."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GeoJSONError(str(exc)) from exc
    validate_geojson(data)
    return data
