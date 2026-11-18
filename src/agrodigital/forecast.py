"""Transparent seasonal time-series forecasts using only the Python standard library.

Outputs are forecasts, not observations. The method is deliberately simple and
must not be interpreted as a validated agronomic or environmental model.
"""
from __future__ import annotations

from datetime import date
from itertools import combinations
from math import isfinite
from statistics import median, pstdev

FORECAST_LABEL = "PRONÓSTICO — estimación estadística, no medición"


def _parse_observations(observations):
    parsed = []
    for row in observations:
        if not isinstance(row, dict) or "date" not in row or "value" not in row:
            raise ValueError("Each observation must contain ISO date and numeric value fields.")
        if isinstance(row["value"], bool):
            raise TypeError("Observation values must be numeric, not booleans.")
        try:
            day = date.fromisoformat(str(row["date"])[:10])
            value = float(row["value"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Observation dates must be ISO dates and values numeric.") from exc
        if not isfinite(value):
            raise ValueError("Observation values must be finite; NaN and infinity are rejected.")
        parsed.append((day, value))
    parsed.sort(key=lambda item: item[0])
    if len(parsed) < 6:
        raise ValueError("At least six observations are required for a seasonal analysis.")
    if len({day for day, _ in parsed}) != len(parsed):
        raise ValueError("Observation dates must be unique.")
    return parsed


def _month_index(day: date) -> int:
    return day.year * 12 + day.month - 1


def _add_months(day: date, offset: int) -> date:
    index = _month_index(day) + offset
    year, month0 = divmod(index, 12)
    return date(year, month0 + 1, min(day.day, 28))


def _theil_sen(x_values, y_values):
    slopes = [(y2 - y1) / (x2 - x1)
              for (x1, y1), (x2, y2) in combinations(zip(x_values, y_values), 2)
              if x2 != x1]
    if not slopes:
        raise ValueError("Cannot estimate a trend from identical time coordinates.")
    slope = median(slopes)
    intercept = median(y - slope * x for x, y in zip(x_values, y_values))
    residuals = [y - (intercept + slope * x) for x, y in zip(x_values, y_values)]
    return slope, intercept, residuals


def _robust_scale(values):
    center = median(values)
    mad = median(abs(value - center) for value in values)
    scale = 1.4826 * mad
    if scale == 0 and len(values) > 1:
        scale = pstdev(values)
    return scale


def _seasonal_fit(rows):
    origin = _month_index(rows[0][0])
    x_values = [_month_index(day) - origin for day, _ in rows]
    values = [value for _, value in rows]
    initial_slope, _, _ = _theil_sen(x_values, values)
    detrended = [value - initial_slope * x for x, value in zip(x_values, values)]
    grouped = {month: [] for month in range(1, 13)}
    for (day, _), value in zip(rows, detrended):
        grouped[day.month].append(value)
    climatology = {month: median(items) for month, items in grouped.items() if items}
    deseasonalized = [value - climatology[day.month] for (day, value) in rows]
    slope, intercept, _ = _theil_sen(x_values, deseasonalized)
    residuals = [value - (intercept + slope * x + climatology[day.month])
                 for (day, value), x in zip(rows, x_values)]
    return origin, x_values, climatology, slope, intercept, residuals


def detect_monthly_anomalies(observations, *, threshold: float = 2.5) -> dict:
    """Flag residual departures after removing robust linear trend and month climatology."""
    rows = _parse_observations(observations)
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not isfinite(float(threshold)) or threshold <= 0:
        raise ValueError("threshold must be a finite positive number.")
    origin, x_values, climatology, slope, intercept, residuals = _seasonal_fit(rows)
    scale = _robust_scale(residuals)
    anomalies = []
    for (day, value), x, residual in zip(rows, x_values, residuals):
        score = residual / scale if scale > 0 else (0.0 if residual == 0 else float("inf"))
        anomalies.append({"date": day.isoformat(), "observed_value": value,
                          "trend_and_seasonal_baseline": intercept + slope * x + climatology[day.month],
                          "residual": residual, "robust_z_score": score,
                          "is_anomaly": abs(score) >= threshold})
    return {"classification": "DERIVADO — detección estadística de anomalías",
            "method": "Theil-Sen linear detrending + calendar-month median climatology + MAD residual score",
            "threshold": threshold, "anomalies": anomalies,
            "limitations": ["Requires repeated observations for calendar months.",
                            "An anomaly is statistical, not a causal diagnosis."]}


def forecast_monthly_series(observations, *, periods: int = 12, interval_z: float = 1.96) -> dict:
    """Forecast monthly values with Theil-Sen trend + monthly residual climatology.

    The seasonal climatology is estimated after an initial robust linear detrend.
    The trend is then refit after removing that monthly seasonal component.
    Intervals use a robust residual scale and widen with forecast horizon.
    """
    rows = _parse_observations(observations)
    if not isinstance(periods, int) or isinstance(periods, bool) or not 1 <= periods <= 120:
        raise ValueError("periods must be an integer from 1 to 120.")
    if isinstance(interval_z, bool) or not isinstance(interval_z, (int, float)) or not isfinite(float(interval_z)) or interval_z <= 0:
        raise ValueError("interval_z must be a finite positive number.")
    origin, x_values, climatology, slope, intercept, residuals = _seasonal_fit(rows)
    residual_scale = _robust_scale(residuals)
    if residual_scale == 0:
        residual_scale = 1e-9

    last_day = rows[-1][0]
    forecasts = []
    for step in range(1, periods + 1):
        target_day = _add_months(last_day, step)
        x = _month_index(target_day) - origin
        seasonal = climatology.get(target_day.month)
        if seasonal is None:
            seasonal = median(climatology.values())
            seasonal_source = "median of available monthly seasonal components; target month absent"
        else:
            seasonal_source = "observed calendar-month median after linear detrending"
        trend_component = intercept + slope * x
        value = trend_component + seasonal
        uncertainty = float(interval_z) * residual_scale * (1.0 + step / max(1, len(rows))) ** 0.5
        forecasts.append({"date": target_day.isoformat(), "forecast_value": value,
                          "lower_bound": value - uncertainty, "upper_bound": value + uncertainty,
                          "trend_component": trend_component, "seasonal_component": seasonal,
                          "seasonal_source": seasonal_source,
                          "interval_method": "approximate robust residual interval; not a calibrated prediction interval"})

    return {"classification": FORECAST_LABEL,
            "method": "monthly seasonal climatology after robust linear detrending + Theil-Sen trend refit",
            "trend_per_month": slope,
            "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "flat",
            "seasonality": {str(month): value for month, value in sorted(climatology.items())},
            "residual_robust_scale": residual_scale, "interval_z": float(interval_z),
            "forecasts": forecasts,
            "assumptions": ["Input is a regularly sampled monthly series; missing months are not interpolated.",
                            "Historical detrended monthly medians represent future seasonality.",
                            "Deseasonalized trend remains linear over the forecast horizon."],
            "limitations": ["Exploratory statistical forecast, not a physical or crop-growth model.",
                            "Intervals are approximate and are not calibrated coverage guarantees.",
                            "Structural breaks, management changes and climate non-stationarity are not modelled.",
                            "Do not use as a substitute for field observations or validated decision models."]}
