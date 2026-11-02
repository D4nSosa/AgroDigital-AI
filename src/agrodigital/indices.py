"""Transparent spectral-index helpers; inputs may be scalars or array-like."""
import math

def normalized_difference(band_a, band_b, *, zero_division=float("nan")):
    """Compute (A-B)/(A+B); NumPy is optional for array inputs."""
    try:
        import numpy as np
    except ImportError:
        return _python_difference(band_a, band_b, zero_division)
    a, b = np.asarray(band_a, dtype=float), np.asarray(band_b, dtype=float)
    denominator = a + b
    result = np.full(np.broadcast(a, b).shape, zero_division, dtype=float)
    np.divide(a - b, denominator, out=result, where=denominator != 0)
    return float(result) if result.ndim == 0 else result

def _python_difference(a, b, zero_division):
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
        if not isinstance(a, (list, tuple)) or not isinstance(b, (list, tuple)):
            raise TypeError("Both inputs must be sequences when either input is a sequence.")
        if len(a) != len(b):
            raise ValueError("Input sequences must have equal lengths.")
        result = [_python_difference(x, y, zero_division) for x, y in zip(a, b)]
        return tuple(result) if isinstance(a, tuple) else result
    denominator = a + b
    return zero_division if denominator == 0 else (a - b) / denominator

def ndvi(nir, red):
    """NDVI = (NIR - Red) / (NIR + Red)."""
    return normalized_difference(nir, red)

def ndwi(green, nir):
    """McFeeters-style NDWI = (Green - NIR) / (Green + NIR)."""
    return normalized_difference(green, nir)
