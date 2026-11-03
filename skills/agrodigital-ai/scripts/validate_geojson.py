#!/usr/bin/env python3
"""Basic GeoJSON structural and coordinate-range validation (Python standard library only)."""
import argparse
import json
import math
import sys
from pathlib import Path

def positions(coords):
    if not isinstance(coords, list):
        return
    if coords and isinstance(coords[0], (int, float)):
        if len(coords) < 2:
            raise ValueError("A position must contain at least longitude and latitude.")
        lon, lat = coords[0], coords[1]
        if not math.isfinite(float(lon)) or not math.isfinite(float(lat)):
            raise ValueError("Coordinates must be finite numbers.")
        if not -180 <= lon <= 180 or not -90 <= lat <= 90:
            raise ValueError(f"Coordinate outside EPSG:4326 range: [{lon}, {lat}]")
        yield (lon, lat)
    else:
        for child in coords:
            yield from positions(child)

def validate(data):
    if not isinstance(data, dict):
        raise ValueError("Top-level GeoJSON must be an object.")
    kind = data.get("type")
    allowed = {"FeatureCollection", "Feature", "Point", "MultiPoint", "LineString",
               "MultiLineString", "Polygon", "MultiPolygon", "GeometryCollection"}
    if kind not in allowed:
        raise ValueError(f"Unsupported or missing GeoJSON type: {kind!r}")
    features = data.get("features", []) if kind == "FeatureCollection" else [data] if kind == "Feature" else []
    geometries = []
    if kind == "FeatureCollection":
        if not isinstance(features, list):
            raise ValueError("'features' must be an array.")
        for i, feature in enumerate(features):
            if not isinstance(feature, dict) or feature.get("type") != "Feature":
                raise ValueError(f"Feature {i} is not a GeoJSON Feature.")
            geometries.append(feature.get("geometry"))
    elif kind == "Feature":
        geometries.append(data.get("geometry"))
    else:
        geometries.append(data)
    count = 0
    for i, geom in enumerate(geometries):
        if geom is None:
            continue
        if not isinstance(geom, dict):
            raise ValueError(f"Geometry {i} must be an object or null.")
        gtype = geom.get("type")
        if gtype == "GeometryCollection":
            nested = geom.get("geometries", [])
            if not isinstance(nested, list):
                raise ValueError("GeometryCollection.geometries must be an array.")
            for child in nested:
                if not isinstance(child, dict):
                    raise ValueError("Invalid child geometry.")
                if "coordinates" in child:
                    count += sum(1 for _ in positions(child["coordinates"]))
        else:
            if gtype not in allowed - {"Feature", "FeatureCollection", "GeometryCollection"}:
                raise ValueError(f"Unsupported geometry type: {gtype!r}")
            if "coordinates" not in geom:
                raise ValueError(f"Geometry {i} has no coordinates.")
            count += sum(1 for _ in positions(geom["coordinates"]))
    if kind in {"Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"} and count == 0:
        raise ValueError("Geometry contains no coordinate positions.")
    return {"valid_structure": True, "geojson_type": kind, "feature_count": len(features),
            "coordinate_positions_checked": count,
            "crs_assumption": "EPSG:4326 longitude/latitude; verify source metadata",
            "limitations": ["Structural/range check only; does not validate topology or calculate area."]}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", help="Input .geojson path")
    p.add_argument("-o", "--output", help="Optional JSON result path")
    args = p.parse_args()
    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = validate(data)
        rendered = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        print(rendered)
    except Exception as exc:
        print(json.dumps({"valid_structure": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)

if __name__ == "__main__":
    main()
