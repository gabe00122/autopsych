from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from typing import Any


REFUSAL_PATTERNS = (
    "i cannot provide",
    "i can't provide",
    "unable to provide",
    "cannot estimate",
    "decline to answer",
)


@dataclass(frozen=True)
class ParseResult:
    status: str
    values: dict[str, Any] | None
    errors: tuple[str, ...] = ()
    recovered_json: bool = False


def _first_json_object(text: str) -> tuple[dict[str, Any], bool]:
    try:
        value = json.loads(text)
        if not isinstance(value, dict):
            raise ValueError("top-level JSON value must be an object")
        return value, False
    except json.JSONDecodeError as direct_error:
        decoder = json.JSONDecoder()
        for index, character in enumerate(text):
            if character != "{":
                continue
            try:
                value, _ = decoder.raw_decode(text[index:])
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                return value, True
        raise direct_error


def _number(value: Any, integer: bool) -> int | float:
    if isinstance(value, bool):
        raise ValueError("boolean is not numeric")
    if isinstance(value, (int, float)):
        parsed = float(value)
    elif isinstance(value, str):
        cleaned = value.strip().replace(",", "").replace("−", "-")
        match = re.fullmatch(
            r"[\s\$£€]*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)(?:\s*[A-Za-z%°/_^0-9.-]+)?\s*",
            cleaned,
        )
        if not match:
            raise ValueError("not a numeric value")
        parsed = float(match.group(1))
    else:
        raise ValueError("not a numeric value")
    if not math.isfinite(parsed):
        raise ValueError("number must be finite")
    if integer:
        if not parsed.is_integer():
            raise ValueError("must be an integer")
        return int(parsed)
    return parsed


def _coerce(value: Any, rule: dict[str, Any]) -> Any:
    allowed = rule.get("type")
    types = allowed if isinstance(allowed, list) else [allowed]
    if value is None and "null" in types:
        return None
    if "number" in types:
        return _number(value, integer=False)
    if "integer" in types:
        return _number(value, integer=True)
    if "string" in types:
        if not isinstance(value, str):
            raise ValueError("must be a string")
        return value
    if "array" in types:
        if not isinstance(value, list):
            raise ValueError("must be an array")
        item_rule = rule.get("items", {})
        return [_coerce(item, item_rule) for item in value]
    if "object" in types:
        if not isinstance(value, dict):
            raise ValueError("must be an object")
        return value
    raise ValueError(f"unsupported schema type: {allowed!r}")


def _validate_rule(name: str, value: Any, rule: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value is None:
        return errors
    if "minLength" in rule and isinstance(value, str) and len(value) < rule["minLength"]:
        errors.append(f"{name} is shorter than minimum length {rule['minLength']}")
    if "maxLength" in rule and isinstance(value, str) and len(value) > rule["maxLength"]:
        errors.append(f"{name} is longer than maximum length {rule['maxLength']}")
    if "minimum" in rule and value < rule["minimum"]:
        errors.append(f"{name} is below minimum {rule['minimum']}")
    if "exclusiveMinimum" in rule and value <= rule["exclusiveMinimum"]:
        errors.append(f"{name} must be greater than {rule['exclusiveMinimum']}")
    if "maximum" in rule and value > rule["maximum"]:
        errors.append(f"{name} exceeds maximum {rule['maximum']}")
    if "enum" in rule and value not in rule["enum"]:
        errors.append(f"{name} is not in the allowed enum")
    return errors


def parse_response(text: str, schema: dict[str, Any]) -> ParseResult:
    lowered = text.lower()
    refusal = any(pattern in lowered for pattern in REFUSAL_PATTERNS)
    try:
        raw, recovered = _first_json_object(text)
    except (json.JSONDecodeError, ValueError) as error:
        status = "refusal" if refusal else "invalid"
        return ParseResult(status=status, values=None, errors=(str(error),))

    required = set(schema.get("required", []))
    properties = schema.get("properties", {})
    errors: list[str] = []
    values: dict[str, Any] = {}
    for name in required:
        if name not in raw:
            errors.append(f"missing required field: {name}")
    if schema.get("additionalProperties") is False:
        extras = sorted(set(raw) - set(properties))
        errors.extend(f"unexpected field: {name}" for name in extras)
    for name, value in raw.items():
        if name not in properties:
            continue
        rule = properties[name]
        try:
            coerced = _coerce(value, rule)
        except (TypeError, ValueError) as error:
            errors.append(f"{name}: {error}")
            continue
        values[name] = coerced
        errors.extend(_validate_rule(name, coerced, rule))

    lower = values.get("interval_lower")
    upper = values.get("interval_upper")
    if lower is not None and upper is not None and lower > upper:
        errors.append("interval_lower exceeds interval_upper")
    if refusal:
        return ParseResult("refusal", values or None, tuple(errors), recovered)
    if errors:
        return ParseResult("invalid", values or None, tuple(errors), recovered)
    return ParseResult("valid", values, (), recovered)
