"""Basic agrometeorological calculations with explicit units."""
from collections.abc import Iterable

def growing_degree_days(tmin_c: float, tmax_c: float, base_c: float, *, upper_c: float | None = None) -> float:
    """Daily mean-method GDD: max(0, min(mean(Tmin,Tmax), upper) - base)."""
    if any(not isinstance(v, (int, float)) for v in (tmin_c, tmax_c, base_c)):
        raise TypeError("Temperatures must be numeric values in degrees Celsius.")
    if tmin_c > tmax_c:
        raise ValueError("tmin_c cannot exceed tmax_c.")
    mean = (tmin_c + tmax_c) / 2
    if upper_c is not None:
        if upper_c < base_c:
            raise ValueError("upper_c cannot be lower than base_c.")
        mean = min(mean, upper_c)
    return max(0.0, mean - base_c)

def rainfall_total(values_mm: Iterable[float], *, ignore_missing: bool = False) -> float:
    """Sum rainfall depths in millimetres; missing values require explicit handling."""
    total = 0.0
    for value in values_mm:
        if value is None:
            if ignore_missing:
                continue
            raise ValueError("Missing rainfall value; use ignore_missing=True explicitly to skip.")
        if not isinstance(value, (int, float)):
            raise TypeError("Rainfall values must be numeric millimetres.")
        if value < 0:
            raise ValueError("Rainfall cannot be negative.")
        total += value
    return total
