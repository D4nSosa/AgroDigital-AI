#!/usr/bin/env python3
"""Create a dependency-free SVG time-series chart from a CSV file."""
import argparse
import csv
import html
import json
from datetime import datetime
from pathlib import Path

WIDTH, HEIGHT = 1000, 560
LEFT, RIGHT, TOP, BOTTOM = 90, 35, 55, 85

def parse_date(value):
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%Y-%m"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise ValueError(f"Unsupported date: {value!r}; use YYYY-MM-DD or YYYY-MM")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", help="CSV containing date and numeric value columns")
    p.add_argument("--date", default="date", help="Date column (default: date)")
    p.add_argument("--value", required=True, help="Numeric value column")
    p.add_argument("--label", help="Chart title/series label")
    p.add_argument("--unit", default="", help="Value unit")
    p.add_argument("-o", "--output", required=True, help="Output SVG path")
    args = p.parse_args()
    rows = []
    with Path(args.input).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = {args.date, args.value} - set(reader.fieldnames or [])
        if missing:
            raise SystemExit("Missing CSV columns: " + ", ".join(sorted(missing)))
        for line, row in enumerate(reader, start=2):
            try:
                rows.append((parse_date(row[args.date]), float(row[args.value])))
            except (ValueError, TypeError) as exc:
                raise SystemExit(f"Invalid data on CSV line {line}: {exc}")
    if len(rows) < 2:
        raise SystemExit("At least two valid observations are required.")
    rows.sort(key=lambda item: item[0])
    if any(not __import__("math").isfinite(v) for _, v in rows):
        raise SystemExit("Values must be finite numbers.")
    x0, x1 = rows[0][0].timestamp(), rows[-1][0].timestamp()
    y_values = [v for _, v in rows]
    ymin, ymax = min(y_values), max(y_values)
    if ymin == ymax:
        pad = max(abs(ymin) * 0.05, 1.0)
        ymin, ymax = ymin - pad, ymax + pad
    else:
        pad = (ymax - ymin) * 0.08
        ymin, ymax = ymin - pad, ymax + pad
    plot_w, plot_h = WIDTH - LEFT - RIGHT, HEIGHT - TOP - BOTTOM
    def sx(d):
        return LEFT + ((d.timestamp() - x0) / (x1 - x0)) * plot_w if x1 != x0 else LEFT + plot_w / 2
    def sy(v):
        return TOP + (ymax - v) / (ymax - ymin) * plot_h
    points = " ".join(f"{sx(d):.1f},{sy(v):.1f}" for d, v in rows)
    title = args.label or args.value
    safe_title = html.escape(title)
    safe_unit = html.escape(args.unit)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{WIDTH/2}" y="30" text-anchor="middle" font-family="sans-serif" font-size="22">{safe_title}</text>']
    for i in range(5):
        y = TOP + i * plot_h / 4
        value = ymax - i * (ymax-ymin) / 4
        parts.append(f'<line x1="{LEFT}" y1="{y:.1f}" x2="{WIDTH-RIGHT}" y2="{y:.1f}" stroke="#dddddd"/>')
        parts.append(f'<text x="{LEFT-12}" y="{y+5:.1f}" text-anchor="end" font-family="sans-serif" font-size="13">{value:.3g}</text>')
    parts += [f'<polyline fill="none" stroke="#1877b8" stroke-width="3" points="{points}"/>']
    for d, v in rows:
        parts.append(f'<circle cx="{sx(d):.1f}" cy="{sy(v):.1f}" r="4" fill="#1877b8"><title>{d.date()}: {v:g}</title></circle>')
    parts += [f'<text x="{LEFT}" y="{HEIGHT-45}" font-family="sans-serif" font-size="13">{rows[0][0].date()}</text>',
              f'<text x="{WIDTH-RIGHT}" y="{HEIGHT-45}" text-anchor="end" font-family="sans-serif" font-size="13">{rows[-1][0].date()}</text>',
              f'<text x="25" y="{HEIGHT/2}" transform="rotate(-90 25 {HEIGHT/2})" text-anchor="middle" font-family="sans-serif" font-size="14">{safe_title} {("(" + safe_unit + ")") if safe_unit else ""}</text>',
              f'<text x="{WIDTH/2}" y="{HEIGHT-12}" text-anchor="middle" font-family="sans-serif" font-size="14">Date</text>',
              '</svg>']
    Path(args.output).write_text("\n".join(parts), encoding="utf-8")
    print(json.dumps({"status":"ok","output":args.output,"observations":len(rows),
                      "start":rows[0][0].date().isoformat(),"end":rows[-1][0].date().isoformat(),
                      "minimum":min(y_values),"maximum":max(y_values)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
