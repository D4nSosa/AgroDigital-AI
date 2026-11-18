"""Illustrative end-to-end forecast example; contains no real field observations."""
from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from agrodigital.forecast import forecast_monthly_series, detect_monthly_anomalies


LABEL = "ILUSTRATIVO — datos sintéticos generados para demostrar el flujo; no son observaciones reales"
SEASONAL = [0, 2, 4, 6, 4, 2, 0, -2, -4, -6, -4, -2]


def build_synthetic_series():
    rows = []
    for year in range(2021, 2024):
        for month in range(1, 13):
            index = (year - 2021) * 12 + month - 1
            value = 50.0 + 0.5 * index + SEASONAL[month - 1]
            rows.append({"date": date(year, month, 1).isoformat(), "value": value})
    # Deliberate synthetic outlier to demonstrate anomaly detection.
    rows[-1]["value"] += 15.0
    return rows


def main():
    observations = build_synthetic_series()
    forecast = forecast_monthly_series(observations, periods=6)
    anomalies = detect_monthly_anomalies(observations)
    output = Path("illustrative_forecast.csv")
    with output.open("w", newline="", encoding="utf-8") as stream:
        fields = ["classification", "date", "forecast_value", "lower_bound", "upper_bound"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in forecast["forecasts"]:
            writer.writerow({"classification": "PRONÓSTICO sobre datos sintéticos ILUSTRATIVOS", **row})
    print(LABEL)
    print("Historical observations:", len(observations))
    print("Forecast classification:", forecast["classification"])
    print("Method:", forecast["method"])
    print("Forecast months:", len(forecast["forecasts"]))
    print("Detected anomaly count:", sum(item["is_anomaly"] for item in anomalies["anomalies"]))
    print("CSV:", output.resolve())
    print("Limitations:", "; ".join(forecast["limitations"]))


if __name__ == "__main__":
    main()
