"""Structural validation for the draft Study 1 Fermi-family roster.

This module deliberately does not validate benchmark correctness. It checks the
design cardinalities and preregistration boundary before any family packet is
allowed to enter the scientific validation workflow.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ELIGIBLE_CLASS_CANDIDATES = {"A_externally_checkable", "B_constructed_triangulated"}
REQUIRED_FAMILY_FIELDS = {
    "family_id",
    "domain",
    "title",
    "status",
    "structure",
    "template",
    "estimand",
    "output_unit",
    "formula",
    "supplied_parameters",
    "bridge_quantities",
    "source_ids",
    "candidate_class",
    "external_back_check",
    "contamination_prior",
    "risks",
    "parameterization_slots",
}
FORBIDDEN_PUBLIC_FAMILY_FIELDS = {
    "prompt",
    "final_stem",
    "final_parameters",
    "benchmark_point",
    "benchmark_interval",
    "constructor_output",
    "challenge_output",
    "wolfram_result",
}


def load_family_roster(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def audit_family_roster(roster: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    families = roster.get("families", [])
    domains = roster.get("registered_domains", [])
    expected_per_domain = roster.get("families_per_domain")
    expected_slots = roster.get("provisional_parameterizations_per_family")
    source_catalog = roster.get("source_catalog", {})

    if roster.get("status") != "draft_roster_unreviewed_not_preregistered":
        errors.append("roster status must preserve the unreviewed, not-preregistered boundary")
    if len(domains) != 5 or len(set(domains)) != 5:
        errors.append("exactly five unique registered domains are required")
    if expected_per_domain != 5:
        errors.append("families_per_domain must equal five")
    if expected_slots != 10:
        errors.append("provisional_parameterizations_per_family must equal ten")
    if len(families) != 25:
        errors.append(f"expected 25 families, found {len(families)}")

    boundary = roster.get("preregistration_boundary", {})
    for field in (
        "final_stems_present",
        "final_numerical_parameters_present",
        "benchmark_values_present",
        "construction_or_review_outputs_present",
        "systematic_wolfram_use_allowed",
    ):
        if boundary.get(field) is not False:
            errors.append(f"preregistration boundary must keep {field}=false")

    family_ids: list[str] = []
    all_slots: list[str] = []
    domain_counts: Counter[str] = Counter()
    structures_by_domain: dict[str, set[str]] = defaultdict(set)

    for family in families:
        family_id = family.get("family_id", "<missing>")
        family_ids.append(family_id)
        missing = REQUIRED_FAMILY_FIELDS - set(family)
        if missing:
            errors.append(f"{family_id}: missing fields {sorted(missing)}")
        forbidden = FORBIDDEN_PUBLIC_FAMILY_FIELDS & set(family)
        if forbidden:
            errors.append(f"{family_id}: forbidden preregistration fields {sorted(forbidden)}")
        if family.get("status") != "draft_roster_unreviewed":
            errors.append(f"{family_id}: status must remain draft_roster_unreviewed")
        domain = family.get("domain")
        if domain not in domains:
            errors.append(f"{family_id}: unregistered domain {domain!r}")
        else:
            domain_counts[domain] += 1
            structures_by_domain[domain].add(family.get("structure", ""))
        if family.get("candidate_class") not in ELIGIBLE_CLASS_CANDIDATES:
            errors.append(f"{family_id}: Class C or unknown class candidate is not eligible")
        if not family.get("supplied_parameters"):
            errors.append(f"{family_id}: at least one supplied parameter is required")
        bridges = family.get("bridge_quantities", [])
        if not bridges or not any(bridge.get("consequential") is True for bridge in bridges):
            errors.append(f"{family_id}: at least one consequential bridge quantity is required")
        for quantity in [*family.get("supplied_parameters", []), *bridges]:
            if not quantity.get("name") or not quantity.get("unit"):
                errors.append(f"{family_id}: every quantity needs a name and unit")
        source_ids = family.get("source_ids", [])
        if not source_ids:
            errors.append(f"{family_id}: at least one source plan is required")
        if family.get("candidate_class") == "B_constructed_triangulated" and len(set(source_ids)) < 2:
            errors.append(f"{family_id}: provisional Class B families require at least two source plans")
        for source_id in source_ids:
            if source_id not in source_catalog:
                errors.append(f"{family_id}: unknown source plan {source_id}")
        slots = family.get("parameterization_slots", [])
        all_slots.extend(slots)
        if len(slots) != expected_slots or len(set(slots)) != expected_slots:
            errors.append(f"{family_id}: expected ten unique parameterization slots")
        expected_prefix = f"{family_id}-P"
        if any(not slot.startswith(expected_prefix) for slot in slots):
            errors.append(f"{family_id}: slot IDs must be namespaced to the family")
        if family.get("contamination_prior") not in {"low", "medium", "high"}:
            errors.append(f"{family_id}: invalid contamination prior")

    if len(set(family_ids)) != len(family_ids):
        errors.append("family IDs must be unique")
    if len(all_slots) != 250 or len(set(all_slots)) != 250:
        errors.append(f"expected 250 unique parameterization slots, found {len(set(all_slots))}")
    for domain in domains:
        if domain_counts[domain] != expected_per_domain:
            errors.append(f"{domain}: expected five families, found {domain_counts[domain]}")
        if len(structures_by_domain[domain]) < 4:
            warnings.append(f"{domain}: fewer than four distinct causal structures")

    located = sum(
        source.get("screen_status") == "official_program_page_located_2026-07-21"
        for source in source_catalog.values()
    )
    unresolved_sources = len(source_catalog) - located
    if unresolved_sources:
        warnings.append(
            f"{unresolved_sources} source catalog entries lack a located official program page "
            "or require packet-specific evidence"
        )
    warnings.append(f"all {len(source_catalog)} source plans still require packet-level verification")

    return {
        "family_count": len(families),
        "domain_counts": dict(domain_counts),
        "parameterization_slot_count": len(all_slots),
        "candidate_classes": dict(Counter(family.get("candidate_class") for family in families)),
        "source_programs": len(source_catalog),
        "source_program_pages_located": located,
        "source_plans_packet_verified": 0,
        "errors": errors,
        "warnings": warnings,
        "passes_structural_validation": not errors,
        "scientific_validation_complete": False,
    }


def audit_family_roster_file(path: Path) -> dict[str, Any]:
    return audit_family_roster(load_family_roster(path))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    roster_path = root / "protocols" / "study1" / "fermi_family_roster.json"
    result = audit_family_roster_file(roster_path)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passes_structural_validation"] else 1)
