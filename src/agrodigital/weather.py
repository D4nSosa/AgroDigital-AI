from collections.abc import Iterable
import math


def _finite_number(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real numeric value in degrees Celsius.")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite (NaN and infinity are not valid).")
    return number


def growing_degree_days(tmin_c: float, tmax_c: float, base_c: float, *, upper_c: float | None = None, method: str = "mean") -> float:
    """Daily GDD in °C·day. mean is the default; modified clips each temperature first."""
    tmin = _finite_number(tmin_c, "tmin_c")
    tmax = _finite_number(tmax_c, "tmax_c")
    base = _finite_number(base_c, "base_c")
    upper = _finite_number(upper_c, "upper_c") if upper_c is not None else None
    if tmin > tmax:
        raise ValueError("tmin_c cannot exceed tmax_c.")
    if upper is not None and upper < base:
        raise ValueError("upper_c cannot be lower than base_c.")
    if method not in {"mean", "modified"}:
        raise ValueError("method must be 'mean' or 'modified'.")
    if method == "modified":
        clipped_min = max(base, tmin)
        clipped_max = max(base, tmax)
        if upper is not None:
            clipped_min = min(clipped_min, upper)
            clipped_max = min(clipped_max, upper)
        return max(0.0, ((clipped_min + clipped_max) / 2.0) - base)
    mean = (tmin + tmax) / 2.0
    if upper is not None:
        mean = min(mean, upper)
    return max(0.0, mean - base)


def rainfall_total(values_mm: Iterable[float], *, ignore_missing: bool = False) -> float:
    """Sum rainfall depths in millimetres; missing values require explicit handling."""
    total = 0.0
    for value in values_mm:
        if value is None:
            if ignore_missing:
                continue
            raise ValueError("Missing rainfall value; use ignore_missing=True explicitly to skip.")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Rainfall values must be numeric millimetres.")
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("Rainfall values must be finite.")
        if number < 0:
            raise ValueError("Rainfall cannot be negative.")
        total += number
    return total
