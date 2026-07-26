"""Deterministic checks for private Study 1 reference-benchmark packets."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path
from typing import Any


def _d(value: Any) -> Decimal:
    return Decimal(str(value))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_phy01_reference_benchmark(
    constructor: dict[str, Any],
    addendum: dict[str, Any],
    slot_ids: list[str],
) -> dict[str, Any]:
    """Audit PHY-01 without treating review readiness as human approval."""

    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, bool] = {}

    checks["family_identity"] = (
        constructor.get("family_id") == addendum.get("family_id") == "PHY-01-SOLAR-YIELD"
    )

    boundary = addendum.get("protocol_boundary", {})
    checks["preregistration_boundary"] = all(
        boundary.get(field) is False
        for field in ("final_stems_present", "final_candidate_parameters_present")
    ) and boundary.get("study_model_runs") == 0

    revised = addendum.get("revised_specification", {})
    checks["area_construct"] = (
        revised.get("area_basis") == "installed_module_surface_area"
        and "aperture" not in revised.get("estimand", "").lower()
        and "gross roof" not in revised.get("estimand", "").lower()
    )
    checks["first_year_scope"] = (
        revised.get("time_scope") == "first_operating_year_typical_meteorological_conditions"
        and revised.get("degradation_treatment") == "no_separate_degradation_term_for_first_year"
    )
    checks["no_duplicate_loss_factor"] = (
        "performance_ratio" not in revised.get("formula", "")
        and revised.get("loss_treatment") == "capacity_factor_includes_system_losses"
    )

    inputs = revised.get("reference_inputs", {})
    area = _d(inputs.get("area_m2", 0))
    density = _d(inputs.get("module_power_density_kW_dc_per_m2", 0))
    hours = _d(inputs.get("hours_per_year", 0))
    cf_point = _d(inputs.get("capacity_factor_point", 0))
    cf_lower = _d(inputs.get("capacity_factor_interval", [0, 0])[0])
    cf_upper = _d(inputs.get("capacity_factor_interval", [0, 0])[1])
    calculated = [area * density * hours * cf / Decimal(1000) for cf in (cf_lower, cf_point, cf_upper)]
    benchmark = revised.get("normalized_reference_benchmark", {})
    recorded = [_d(value) for value in [*benchmark.get("interval_exact", [0, 0])[:1], benchmark.get("point_exact", 0), *benchmark.get("interval_exact", [0, 0])[1:]]]
    checks["arithmetic"] = calculated == recorded
    checks["interval_ordering"] = calculated[0] <= calculated[1] <= calculated[2]
    checks["reported_precision"] = (
        benchmark.get("point_display") == "0.275"
        and benchmark.get("interval_display") == ["0.221", "0.345"]
    )

    weighting = addendum.get("mean_weighting_reproduction", {})
    classes = weighting.get("classes", [])
    weighted = sum(_d(row["capacity_factor"]) * _d(row["population"]) for row in classes)
    population = sum(_d(row["population"]) for row in classes)
    reproduced_mean = weighted / population if population else Decimal(0)
    checks["mean_weighting"] = (
        len(classes) == 10
        and reproduced_mean == _d(weighting.get("weighted_mean_exact", 0))
        and reproduced_mean.quantize(Decimal("0.001")) == cf_point
    )

    elasticities = constructor.get("sensitivity_analysis", [])
    checks["multiplicative_sensitivity"] = (
        len(elasticities) == 3
        and all(_d(item.get("local_elasticity", 0)) == Decimal(1) for item in elasticities)
    )

    sources = addendum.get("evidence_manifest", [])
    checks["source_fields"] = bool(sources) and all(
        source.get("source_id")
        and source.get("publisher")
        and source.get("url")
        and source.get("stable_locator")
        and source.get("facts_used")
        and source.get("limitations") is not None
        for source in sources
    )
    publisher_groups = {source.get("publisher_group") for source in sources}
    checks["organizational_triangulation"] = {"NREL", "LBNL", "CPUC_Itron"}.issubset(
        publisher_groups
    )
    checks["source_roles_bounded"] = all(
        source.get("role") != "independent_national_ground_truth" for source in sources
    )

    checks["discrepancies_builder_resolved"] = not addendum.get("unresolved_builder_discrepancies")
    checks["symbolic_slot_propagation"] = (
        len(slot_ids) == 10
        and len(set(slot_ids)) == 10
        and all(slot.startswith("PHY-01-SOLAR-YIELD-P") for slot in slot_ids)
    )

    for name, passed in checks.items():
        if not passed:
            errors.append(f"failed deterministic check: {name}")

    warnings.extend(
        [
            "Numerical candidate propagation is blocked because final parameterizations do not yet exist.",
            "EIA generation is model-estimated partly with NREL inputs and is not independent ground truth.",
            "The CPUC observed comparison is old, California-specific, and its capacity denominator needs human confirmation.",
            "Human source/construct approval and mandatory second-human adjudication remain incomplete.",
        ]
    )
    family_checks_pass = not errors
    return {
        "family_id": "PHY-01-SOLAR-YIELD",
        "checks": checks,
        "calculated": {
            "weighted_capacity_factor": str(reproduced_mean),
            "benchmark_lower_exact": str(calculated[0]),
            "benchmark_point_exact": str(calculated[1]),
            "benchmark_upper_exact": str(calculated[2]),
        },
        "errors": errors,
        "warnings": warnings,
        "family_level_deterministic_checks_pass": family_checks_pass,
        "symbolic_propagation_checks_pass": checks["symbolic_slot_propagation"],
        "numerical_candidate_propagation_status": "blocked_final_parameters_absent",
        "human_review_status": "pending",
        "retention_eligible": False,
        "scientific_validation_complete": False,
    }


def audit_phy01_reference_benchmark_files(
    constructor_path: Path,
    challenge_path: Path,
    addendum_path: Path,
    roster_path: Path,
) -> dict[str, Any]:
    constructor = json.loads(constructor_path.read_text(encoding="utf-8"))
    addendum = json.loads(addendum_path.read_text(encoding="utf-8"))
    roster = json.loads(roster_path.read_text(encoding="utf-8"))
    family = next(item for item in roster["families"] if item["family_id"] == "PHY-01-SOLAR-YIELD")
    result = audit_phy01_reference_benchmark(constructor, addendum, family["parameterization_slots"])

    bindings = addendum.get("bindings", {})
    result["bindings_verified"] = {
        "constructor_sha256": _sha256(constructor_path) == bindings.get("constructor_sha256"),
        "challenge_sha256": _sha256(challenge_path) == bindings.get("challenge_sha256"),
    }
    if not all(result["bindings_verified"].values()):
        result["errors"].append("post-freeze addendum binding hash mismatch")
        result["family_level_deterministic_checks_pass"] = False
    return result
