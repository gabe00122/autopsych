from __future__ import annotations


_UNITS: dict[str, tuple[str, float]] = {
    "m": ("length", 1.0),
    "meter": ("length", 1.0),
    "meters": ("length", 1.0),
    "km": ("length", 1000.0),
    "cm": ("length", 0.01),
    "ft": ("length", 0.3048),
    "kg": ("mass", 1.0),
    "g": ("mass", 0.001),
    "lb": ("mass", 0.45359237),
    "l": ("volume", 1.0),
    "liter": ("volume", 1.0),
    "liters": ("volume", 1.0),
    "ml": ("volume", 0.001),
    "m3": ("volume", 1000.0),
    "m^3": ("volume", 1000.0),
    "wh": ("energy", 1.0),
    "kwh": ("energy", 1000.0),
    "mwh": ("energy", 1_000_000.0),
    "second": ("time", 1.0),
    "seconds": ("time", 1.0),
    "minute": ("time", 60.0),
    "minutes": ("time", 60.0),
    "hour": ("time", 3600.0),
    "hours": ("time", 3600.0),
    "day": ("time", 86400.0),
    "days": ("time", 86400.0),
}


def convert(value: float, source: str, target: str) -> float:
    source_key = source.strip().lower()
    target_key = target.strip().lower()
    if source_key == target_key:
        return float(value)
    if source_key not in _UNITS or target_key not in _UNITS:
        raise ValueError(f"unsupported unit conversion: {source!r} to {target!r}")
    source_dimension, source_factor = _UNITS[source_key]
    target_dimension, target_factor = _UNITS[target_key]
    if source_dimension != target_dimension:
        raise ValueError(f"incompatible units: {source!r} and {target!r}")
    return float(value) * source_factor / target_factor
