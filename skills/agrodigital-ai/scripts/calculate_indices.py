#!/usr/bin/env python3
"""Calculate NDVI and/or Green-NIR NDWI from supplied CSV band values."""
import argparse
import csv
import json
from pathlib import Path

def ratio(a, b):
    denominator = a + b
    return None if denominator == 0 else (a - b) / denominator

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", help="CSV with nir and red columns; green is optional")
    p.add_argument("-o", "--output", required=True, help="Output CSV path")
    p.add_argument("--ndwi", action="store_true", help="Also calculate McFeeters NDWI (green-NIR)")
    args = p.parse_args()
    src, dst = Path(args.input), Path(args.output)
    with src.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        required = {"nir", "red"} | ({"green"} if args.ndwi else set())
        missing = required - set(fields)
        if missing:
            raise SystemExit(f"Missing CSV columns: {', '.join(sorted(missing))}")
        out_fields = list(fields) + ["ndvi"] + (["ndwi_mcfeeters"] if args.ndwi else [])
        rows = []
        for line, row in enumerate(reader, start=2):
            try:
                nir, red = float(row["nir"]), float(row["red"])
                row["ndvi"] = "" if nir + red == 0 else f"{ratio(nir, red):.8f}"
                if args.ndwi:
                    green = float(row["green"])
                    row["ndwi_mcfeeters"] = "" if green + nir == 0 else f"{ratio(green, nir):.8f}"
            except (TypeError, ValueError) as exc:
                raise SystemExit(f"Invalid numeric value on CSV line {line}: {exc}")
            rows.append(row)
    with dst.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"status":"ok","input":str(src),"output":str(dst),"rows":len(rows),
                      "indices":["NDVI"] + (["NDWI McFeeters"] if args.ndwi else []),
                      "warning":"Calculates indices only from supplied band values; no imagery is downloaded, calibrated, masked or georeferenced."}, ensure_ascii=False))

if __name__ == "__main__":
    main()
