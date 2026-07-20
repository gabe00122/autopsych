from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .ledger import read_jsonl


REQUIRED_TERMINAL_FIELDS = {
    "run_id",
    "trial_id",
    "model_id",
    "provider",
    "started_at",
    "completed_at",
    "prompt_hash",
    "messages",
    "sampling",
    "attempts",
    "raw_response",
    "parse_status",
    "parsed_values",
    "scoring_results",
    "error",
}


def audit_run(manifest_path: Path, records_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    intended = list(manifest["intended_trial_ids"])
    records = [record for record in read_jsonl(records_path) if record.get("record_type") == "trial_result"]
    counts = Counter(record.get("trial_id") for record in records)
    complete_ids = {
        record["trial_id"]
        for record in records
        if record.get("trial_id") in intended and REQUIRED_TERMINAL_FIELDS <= set(record)
    }
    missing = sorted(set(intended) - complete_ids)
    unexpected = sorted(set(counts) - set(intended) - {None})
    duplicates = sorted(trial_id for trial_id, count in counts.items() if trial_id and count > 1)
    completeness = len(complete_ids) / len(intended) if intended else 0.0
    return {
        "run_id": manifest["run_id"],
        "intended": len(intended),
        "complete": len(complete_ids),
        "completeness": completeness,
        "passes_99_percent": completeness >= 0.99,
        "passes_integrity": completeness >= 0.99 and not unexpected and not duplicates,
        "missing_trial_ids": missing,
        "unexpected_trial_ids": unexpected,
        "duplicate_trial_ids": duplicates,
    }


def evaluate_study0(metrics: dict[str, float], rubric: dict[str, Any]) -> dict[str, Any]:
    criteria = {
        "synthetic_accuracy": metrics["synthetic_accuracy"] >= rubric["synthetic_accuracy_min"],
        "human_autopsych_agreement": metrics["human_autopsych_agreement"]
        >= rubric["human_autopsych_agreement_min"],
        "directional_replications": metrics["directional_replications"]
        >= rubric["directional_replications_min"],
        "run_completeness": metrics["run_completeness"] >= rubric["run_completeness_min"],
    }
    passed = sum(criteria.values())
    decision = "validated" if passed == 4 else "remediate_before_study1" if passed == 3 else "full_pipeline_audit"
    return {"criteria": criteria, "passed": passed, "decision": decision}
