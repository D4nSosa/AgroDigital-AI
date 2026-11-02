"""Command-line interface for the portable geospatial core."""
import argparse, json, sys
from pathlib import Path
from .core import inspect_python_capabilities
from .geo import GeoJSONError, load_geojson, validate_geojson
from .weather import growing_degree_days, rainfall_total


def build_parser():
    parser = argparse.ArgumentParser(prog="agrodigital", description="AgroDigital-AI portable tools")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check-geojson", help="Validate GeoJSON structure and coordinate ranges")
    check.add_argument("path")

    gdd = sub.add_parser("gdd", help="Calculate approximate daily GDD")
    gdd.add_argument("--tmin", type=float, required=True)
    gdd.add_argument("--tmax", type=float, required=True)
    gdd.add_argument("--base", type=float, required=True)
    gdd.add_argument("--upper", type=float)

    rain = sub.add_parser("rainfall", help="Sum rainfall values in millimetres")
    rain.add_argument("values", nargs="+", type=float)
    sub.add_parser("capabilities", help="List optional Python modules detected")

    info = sub.add_parser("raster-info", help="Inspect GeoTIFF metadata")
    info.add_argument("input")

    index = sub.add_parser("raster-index", help="Write a normalized-difference GeoTIFF")
    index.add_argument("input"); index.add_argument("output")
    index.add_argument("--band-a", type=int, required=True)
    index.add_argument("--band-b", type=int, required=True)
    index.add_argument("--label", default="normalized_difference")

    clip = sub.add_parser("raster-clip", help="Clip/mask raster with an RFC 7946 GeoJSON AOI")
    clip.add_argument("input"); clip.add_argument("aoi"); clip.add_argument("output")
    clip.add_argument("--no-crop", action="store_true")

    reproj = sub.add_parser("raster-reproject", help="Reproject raster to an explicit target CRS")
    reproj.add_argument("input"); reproj.add_argument("output"); reproj.add_argument("--target-crs", required=True)

    vector = sub.add_parser("vector-reproject", help="Reproject GeoJSON with explicit source and target CRS")
    vector.add_argument("input"); vector.add_argument("output")
    vector.add_argument("--source-crs", required=True); vector.add_argument("--target-crs", required=True)

    topology = sub.add_parser("vector-validate", help="Validate vector geometry topology with Shapely")
    topology.add_argument("input")

    stac = sub.add_parser("stac-search", help="Search public STAC metadata (does not download imagery)")
    area = stac.add_mutually_exclusive_group(required=True)
    area.add_argument("--bbox", nargs=4, type=float, metavar=("WEST", "SOUTH", "EAST", "NORTH"))
    area.add_argument("--intersects", help="Path to GeoJSON geometry/Feature/FeatureCollection")
    stac.add_argument("--datetime", help="RFC3339 instant or interval")
    stac.add_argument("--collections", nargs="+", default=["sentinel-2-l2a"])
    stac.add_argument("--max-items", type=int, default=20)
    stac.add_argument("--cloud-cover-max", type=float)
    stac.add_argument("--endpoint", default="https://earth-search.aws.element84.com/v1")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "check-geojson":
            result = validate_geojson(load_geojson(args.path))
        elif args.command == "gdd":
            result = {"gdd_degree_days": growing_degree_days(args.tmin, args.tmax, args.base, upper_c=args.upper),
                      "method": "daily mean temperature", "unit": "°C·day"}
        elif args.command == "rainfall":
            result = {"rainfall_total_mm": rainfall_total(args.values), "unit": "mm"}
        elif args.command == "capabilities":
            result = inspect_python_capabilities().to_dict()
        elif args.command == "raster-info":
            from .raster import inspect_raster
            result = inspect_raster(args.input)
        elif args.command == "raster-index":
            from .raster import calculate_normalized_difference
            result = calculate_normalized_difference(args.input, args.output, args.band_a, args.band_b, label=args.label)
        elif args.command == "raster-clip":
            from .raster import clip_raster
            result = clip_raster(args.input, args.aoi, args.output, crop=not args.no_crop)
        elif args.command == "raster-reproject":
            from .raster import reproject_raster
            result = reproject_raster(args.input, args.output, args.target_crs)
        elif args.command == "vector-reproject":
            from .vector import reproject_geojson
            result = reproject_geojson(args.input, args.output, args.source_crs, args.target_crs)
        elif args.command == "vector-validate":
            from .vector import validate_topology
            result = validate_topology(args.input)
        elif args.command == "stac-search":
            from .stac import search_stac
            intersects = json.loads(Path(args.intersects).read_text(encoding="utf-8")) if args.intersects else None
            result = search_stac(bbox=args.bbox, intersects=intersects, datetime=args.datetime,
                                 collections=args.collections, max_items=args.max_items,
                                 cloud_cover_max=args.cloud_cover_max, endpoint=args.endpoint)
        else:
            raise ValueError(f"Unsupported command: {args.command}")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (GeoJSONError, ValueError, TypeError, OSError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
