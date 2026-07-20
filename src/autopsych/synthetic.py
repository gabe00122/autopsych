from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .parsing import parse_response
from .scoring import score_fermi


PRODUCTION_SCHEMA_PATHS = {
    "study0-response": Path("protocols/study0/response.schema.json"),
    "study1-track-a": Path("protocols/study1/track_a.schema.json"),
    "study1-track-b": Path("protocols/study1/track_b.schema.json"),
    "study1-revision": Path("protocols/study1/revision.schema.json"),
}


def synthetic_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["estimate", "units", "interval_lower", "interval_upper", "confidence_within_1_order"],
        "properties": {
            "estimate": {"type": "number", "exclusiveMinimum": 0},
            "units": {"type": "string"},
            "interval_lower": {"type": "number", "exclusiveMinimum": 0},
            "interval_upper": {"type": "number", "exclusiveMinimum": 0},
            "confidence_within_1_order": {"type": "integer", "minimum": 0, "maximum": 100},
        },
    }


def generate_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for index in range(500):
        variant = index % 10
        base = float(index + 10)
        valid = {
            "estimate": base,
            "units": "kg",
            "interval_lower": base / 2,
            "interval_upper": base * 2,
            "confidence_within_1_order": 75,
        }
        if variant == 0:
            text, expected = json.dumps(valid), "valid"
        elif variant == 1:
            valid["estimate"] = base + 0.125
            text, expected = json.dumps(valid), "valid"
        elif variant == 2:
            valid["estimate"] = f"{base:.3e}"
            text, expected = json.dumps(valid), "valid"
        elif variant == 3:
            valid["estimate"] = f"{base * 1000:,.0f} kg"
            text, expected = "Ignore this wrapper and parse the object:\n```json\n" + json.dumps(valid) + "\n```", "valid"
        elif variant == 4:
            valid.pop("estimate")
            text, expected = json.dumps(valid), "invalid"
        elif variant == 5:
            text, expected = '{"estimate": 12, "units": "kg"', "invalid"
        elif variant == 6:
            valid["confidence_within_1_order"] = 120
            text, expected = json.dumps(valid), "invalid"
        elif variant == 7:
            valid["interval_lower"], valid["interval_upper"] = base * 2, base / 2
            text, expected = json.dumps(valid), "invalid"
        elif variant == 8:
            text, expected = "I cannot estimate this quantity reliably.", "refusal"
        else:
            valid["units"] = "kg·yr⁻¹"
            text = "  \n" + json.dumps(valid, ensure_ascii=False) + "\n  "
            expected = "valid"
        cases.append({"case_id": f"synthetic-{index:03d}", "text": text, "expected_status": expected})
    return cases


def write_cases(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for case in generate_cases():
            handle.write(json.dumps(case, ensure_ascii=False) + "\n")


def validate_cases(path: Path) -> dict[str, Any]:
    cases = []
    with path.open(encoding="utf-8") as handle:
        cases = [json.loads(line) for line in handle if line.strip()]
    correct = 0
    failures = []
    schema = synthetic_schema()
    for case in cases:
        actual = parse_response(case["text"], schema).status
        if actual == case["expected_status"]:
            correct += 1
        else:
            failures.append({"case_id": case["case_id"], "expected": case["expected_status"], "actual": actual})
    accuracy = correct / len(cases) if cases else 0.0
    return {"n": len(cases), "correct": correct, "accuracy": accuracy, "passes_98_percent": accuracy >= 0.98, "failures": failures}


def _matches_gold(actual: Any, expected: Any) -> bool:
    if isinstance(expected, float) and isinstance(actual, (int, float)):
        return math.isclose(float(actual), expected, rel_tol=1e-12, abs_tol=1e-12)
    if isinstance(expected, dict) and isinstance(actual, dict):
        return all(key in actual and _matches_gold(actual[key], value) for key, value in expected.items())
    if isinstance(expected, list) and isinstance(actual, list):
        return len(actual) == len(expected) and all(_matches_gold(left, right) for left, right in zip(actual, expected))
    return actual == expected


def _read_gold_cases(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _repository_root(path: Path) -> Path:
    for parent in (path.parent, *path.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    raise ValueError(f"could not locate repository root for gold corpus: {path}")


def validate_gold_cases(path: Path) -> dict[str, Any]:
    """Validate independent parse and score expectations from a frozen gold corpus."""

    cases = _read_gold_cases(path)
    repository_root = _repository_root(path)
    correct = 0
    failures: list[dict[str, str]] = []
    schema_ids = set()

    for case in cases:
        case_id = case.get("case_id", "<missing case_id>")
        schema_id = case.get("schema_id")
        schema_relative_path = PRODUCTION_SCHEMA_PATHS.get(schema_id)
        if schema_relative_path is None:
            failures.append({"case_id": case_id, "reason": f"unknown schema_id: {schema_id!r}"})
            continue
        schema_ids.add(schema_id)
        schema_path = repository_root / schema_relative_path
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        parsed = parse_response(case["text"], schema)
        expected = case["expected"]
        mismatch: str | None = None
        if parsed.status != expected["status"]:
            mismatch = f"status expected {expected['status']!r}, got {parsed.status!r}"
        elif "values" in expected and not _matches_gold(parsed.values, expected["values"]):
            mismatch = f"values expected {expected['values']!r}, got {parsed.values!r}"
        elif "recovered_json" in expected and parsed.recovered_json != expected["recovered_json"]:
            mismatch = f"recovered_json expected {expected['recovered_json']!r}, got {parsed.recovered_json!r}"
        elif any(fragment not in " ".join(parsed.errors) for fragment in expected.get("error_substrings", [])):
            mismatch = f"errors did not contain {expected['error_substrings']!r}: {parsed.errors!r}"
        elif "scoring" in case:
            scoring_spec = case["scoring"]
            try:
                score = score_fermi(
                    parsed.values or {},
                    truth=scoring_spec["truth"],
                    expected_unit=scoring_spec.get("expected_unit"),
                    truth_interval=tuple(scoring_spec["truth_interval"]) if "truth_interval" in scoring_spec else None,
                )
            except (KeyError, TypeError, ValueError) as error:
                expected_error = scoring_spec.get("expected_error")
                if expected_error is None or expected_error not in str(error):
                    mismatch = f"scoring raised {type(error).__name__}: {error}"
            else:
                if "expected_error" in scoring_spec:
                    mismatch = "scoring succeeded but an error was expected"
                elif not _matches_gold(score, scoring_spec["expected"]):
                    mismatch = f"score expected {scoring_spec['expected']!r}, got {score!r}"
        if mismatch:
            failures.append({"case_id": case_id, "reason": mismatch})
        else:
            correct += 1

    accuracy = correct / len(cases) if cases else 0.0
    return {
        "n": len(cases),
        "correct": correct,
        "accuracy": accuracy,
        "passes_98_percent": accuracy >= 0.98,
        "schemas_covered": sorted(schema_ids),
        "failures": failures,
    }
