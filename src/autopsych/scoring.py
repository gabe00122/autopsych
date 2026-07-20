from __future__ import annotations

import math
from typing import Any

from .units import convert


def _positive(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be positive and finite")
    return value


def score_fermi(
    values: dict[str, Any],
    truth: float,
    expected_unit: str | None = None,
    truth_interval: tuple[float, float] | None = None,
) -> dict[str, Any]:
    estimate = _positive(values["estimate"], "estimate")
    if expected_unit is not None:
        estimate = convert(estimate, values["units"], expected_unit)
    truth = _positive(truth, "truth")
    signed_log_error = math.log10(estimate / truth)
    absolute_log_error = abs(signed_log_error)
    result: dict[str, Any] = {
        "normalized_estimate": estimate,
        "signed_log10_error": signed_log_error,
        "absolute_log10_error": absolute_log_error,
        "within_one_order": absolute_log_error <= 1.0,
    }
    if truth_interval is not None:
        lower, upper = truth_interval
        if not 0 < lower <= upper:
            raise ValueError("truth interval must be positive and ordered")
        if lower <= estimate <= upper:
            interval_error = 0.0
        elif estimate < lower:
            interval_error = math.log10(lower / estimate)
        else:
            interval_error = math.log10(estimate / upper)
        result["truth_interval_log10_error"] = interval_error
    if values.get("interval_lower") is not None and values.get("interval_upper") is not None:
        lower = float(values["interval_lower"])
        upper = float(values["interval_upper"])
        if expected_unit is not None:
            lower = convert(lower, values["units"], expected_unit)
            upper = convert(upper, values["units"], expected_unit)
        result["stated_interval_contains_truth"] = lower <= truth <= upper
    confidence = values.get("confidence_within_1_order")
    if confidence is not None:
        probability = float(confidence) / 100.0
        outcome = float(result["within_one_order"])
        result["brier_within_one_order"] = (probability - outcome) ** 2
    return result


def score_revision(original: float, revised: float, truth: float) -> dict[str, Any]:
    original_error = abs(math.log10(_positive(original, "original") / _positive(truth, "truth")))
    revised_error = abs(math.log10(_positive(revised, "revised") / truth))
    delta = original_error - revised_error
    direction = "toward_truth" if delta > 0 else "away_from_truth" if delta < 0 else "unchanged"
    return {
        "original_absolute_log10_error": original_error,
        "revised_absolute_log10_error": revised_error,
        "improvement_log10": delta,
        "revision_direction": direction,
    }
