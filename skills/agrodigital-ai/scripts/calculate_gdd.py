#!/usr/bin/env python3
"""Calculate daily growing degree days from a CSV with tmin_c and tmax_c columns."""
import argparse
import csv
import json
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", help="CSV containing tmin_c,tmax_c columns")
    p.add_argument("-o", "--output", required=True, help="Output CSV path")
    p.add_argument("--base", type=float, required=True, help="Base temperature in Celsius")
    p.add_argument("--upper", type=float, help="Optional upper cap in Celsius")
    args = p.parse_args()
    if args.upper is not None and args.upper < args.base:
        p.error("--upper must be greater than or equal to --base")
    src, dst = Path(args.input), Path(args.output)
    rows = []
    with src.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = {"tmin_c", "tmax_c"} - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"Missing CSV columns: {', '.join(sorted(missing))}")
        cumulative = 0.0
        for line, row in enumerate(reader, start=2):
            try:
                tmin, tmax = float(row["tmin_c"]), float(row["tmax_c"])
            except (TypeError, ValueError) as exc:
                raise SystemExit(f"Invalid temperature on CSV line {line}: {exc}")
            if tmin > tmax:
                raise SystemExit(f"tmin_c exceeds tmax_c on CSV line {line}")
            mean = (tmin + tmax) / 2
            effective = min(mean, args.upper) if args.upper is not None else mean
            daily = max(0.0, effective - args.base)
            cumulative += daily
            row["gdd_daily_c_day"] = f"{daily:.4f}"
            row["gdd_cumulative_c_day"] = f"{cumulative:.4f}"
            rows.append(row)
    fields = list(rows[0].keys()) if rows else ["tmin_c","tmax_c","gdd_daily_c_day","gdd_cumulative_c_day"]
    with dst.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"status":"ok","output":str(dst),"days":len(rows),"base_c":args.base,
                      "upper_c":args.upper,"cumulative_gdd_c_day":round(cumulative,4),
                      "method":"max(0, mean(Tmin,Tmax) capped at upper if supplied minus base)"}))

if __name__ == "__main__":
    main()
