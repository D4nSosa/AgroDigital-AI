"""Command-line interface for the portable core."""
import argparse, json, sys
from .core import inspect_python_capabilities
from .geo import GeoJSONError, load_geojson, validate_geojson
from .weather import growing_degree_days, rainfall_total

def build_parser():
    parser = argparse.ArgumentParser(prog="agrodigital", description="AgroDigital-AI portable tools")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check-geojson", help="Validate a GeoJSON file"); check.add_argument("path")
    gdd = sub.add_parser("gdd", help="Calculate approximate daily GDD")
    gdd.add_argument("--tmin", type=float, required=True); gdd.add_argument("--tmax", type=float, required=True)
    gdd.add_argument("--base", type=float, required=True); gdd.add_argument("--upper", type=float)
    rain = sub.add_parser("rainfall", help="Sum rainfall values in millimetres"); rain.add_argument("values", nargs="+", type=float)
    sub.add_parser("capabilities", help="List optional Python modules detected")
    return parser

def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "check-geojson": result = validate_geojson(load_geojson(args.path))
        elif args.command == "gdd":
            result = {"gdd_degree_days": growing_degree_days(args.tmin, args.tmax, args.base, upper_c=args.upper), "method": "daily mean temperature", "unit": "°C·day"}
        elif args.command == "rainfall": result = {"rainfall_total_mm": rainfall_total(args.values), "unit": "mm"}
        else: result = inspect_python_capabilities().to_dict()
        print(json.dumps(result, indent=2, ensure_ascii=False)); return 0
    except (GeoJSONError, ValueError, TypeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 2

if __name__ == "__main__": raise SystemExit(main())
