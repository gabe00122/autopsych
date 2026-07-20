from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .audit import audit_run
from .ledger import read_jsonl


SCHEMA_VERSION = "1.0"
SOURCE = "autopsych"
PHASE_LABELS = {
    "protocol_freeze": "Protocol freeze",
    "study0_validation": "Study 0 validation",
    "study1_pilot_and_preregistration": "Study 1 pilot and preregistration",
    "study1_collection": "Study 1 collection",
    "locked_analysis": "Locked analysis",
    "release": "Release",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def _git_value(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def _study_bucket(value: Any) -> str | None:
    normalized = str(value or "").lower().replace("-", "_").replace(" ", "_")
    if "study0" in normalized or "study_0" in normalized:
        return "study0"
    if "track_a" in normalized:
        return "track_a"
    if "track_b" in normalized:
        return "track_b"
    return None


def _run_summary(manifest_path: Path) -> dict[str, Any]:
    manifest = _read_json(manifest_path)
    records_path = manifest_path.with_name("records.jsonl")
    records = read_jsonl(records_path)
    terminal_records = [record for record in records if record.get("record_type") == "trial_result"]
    audit = audit_run(manifest_path, records_path)
    trials = manifest.get("trials") or []
    study = next((trial.get("study") for trial in trials if isinstance(trial, dict) and trial.get("study")), None)
    if study is None:
        study = next((record.get("study") for record in terminal_records if record.get("study")), None)
    return {
        "run_id": str(manifest.get("run_id") or manifest_path.parent.name),
        "study": study,
        "study_bucket": _study_bucket(study),
        "protocol_id": manifest.get("protocol_id"),
        "created_at": manifest.get("created_at"),
        "intended": audit["intended"],
        "complete": audit["complete"],
        "completeness": audit["completeness"],
        "passes_integrity": audit["passes_integrity"],
        "api_errors": sum(1 for record in terminal_records if record.get("error")),
        "parse_failures": sum(
            1
            for record in terminal_records
            if record.get("parse_status") not in {"valid", "refusal"}
        ),
        "missing": len(audit["missing_trial_ids"]),
        "unexpected": len(audit["unexpected_trial_ids"]),
        "duplicates": len(audit["duplicate_trial_ids"]),
    }


def _call_counts(protocol: dict[str, Any], runs: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    targets = {
        "study0": int(protocol.get("study0", {}).get("total_calls", 0)),
        "track_a": int(protocol.get("study1", {}).get("track_a_calls", 0)),
        "track_b": int(protocol.get("study1", {}).get("track_b_calls", 0)),
    }
    complete = {key: 0 for key in targets}
    for run in runs:
        bucket = run.get("study_bucket")
        if bucket in complete:
            complete[bucket] += int(run.get("complete") or 0)
    return {
        key: {"complete": min(complete[key], target) if target else complete[key], "intended": target}
        for key, target in targets.items()
    }


def _current_phase(
    protocol: dict[str, Any],
    calls: dict[str, dict[str, int]],
    acceptance: dict[str, Any] | None,
) -> dict[str, str | None]:
    protocol_status = str(protocol.get("status") or "unknown")
    frozen_statuses = {"frozen", "preregistered", "registered", "active"}
    if protocol_status not in frozen_statuses:
        phase = "protocol_freeze"
        reason = f"Protocol status is {protocol_status}."
    elif calls["study0"]["complete"] < calls["study0"]["intended"]:
        phase = "study0_validation"
        reason = "Study 0 intended calls are not complete."
    elif not acceptance or acceptance.get("decision") != "validated":
        phase = "study0_validation"
        reason = "Study 0 acceptance has not been recorded as validated."
    elif calls["track_a"]["complete"] == 0 and calls["track_b"]["complete"] == 0:
        phase = "study1_pilot_and_preregistration"
        reason = "Study 0 passed; Study 1 collection has not started."
    elif (
        calls["track_a"]["complete"] < calls["track_a"]["intended"]
        or calls["track_b"]["complete"] < calls["track_b"]["intended"]
    ):
        phase = "study1_collection"
        reason = "Study 1 collection is in progress."
    else:
        phase = "locked_analysis"
        reason = "All intended Study 1 calls are complete."
    return {"current_id": phase, "label": PHASE_LABELS[phase], "reason": reason}


def build_execution_snapshot(root: Path) -> dict[str, Any]:
    root = root.resolve()
    protocol_path = root / "protocols" / "year1_protocol.json"
    if not protocol_path.exists():
        raise FileNotFoundError(f"missing protocol: {protocol_path}")
    protocol = _read_json(protocol_path)
    runs_root = root / "runs"
    runs = []
    warnings: list[str] = []
    if runs_root.exists():
        for manifest_path in sorted(runs_root.glob("*/manifest.json")):
            try:
                runs.append(_run_summary(manifest_path))
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
                warnings.append(f"Could not summarize run {manifest_path.parent.name}: {error}")

    acceptance_path = runs_root / "study0_acceptance.json"
    acceptance = _read_json(acceptance_path) if acceptance_path.exists() else None
    calls = _call_counts(protocol, runs)
    commit = _git_value(root, "rev-parse", "HEAD")
    porcelain = _git_value(root, "status", "--porcelain")
    dirty = None if porcelain is None else bool(porcelain)

    integrity_failures = sum(1 for run in runs if not run["passes_integrity"])
    api_errors = sum(int(run["api_errors"]) for run in runs)
    parse_failures = sum(int(run["parse_failures"]) for run in runs)
    if integrity_failures:
        warnings.append(f"{integrity_failures} run(s) currently fail completeness or integrity checks.")
    if api_errors:
        warnings.append(f"{api_errors} terminal record(s) contain API errors.")
    if parse_failures:
        warnings.append(f"{parse_failures} terminal record(s) contain parse failures.")

    return {
        "schema_version": SCHEMA_VERSION,
        "source": SOURCE,
        "generated_at": _utc_now(),
        "repository": {
            "commit_sha": commit,
            "dirty": dirty,
        },
        "protocol": {
            "id": protocol.get("protocol_id"),
            "status": protocol.get("status"),
            "sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
            "project_start": protocol.get("project_period", {}).get("start"),
            "project_end": protocol.get("project_period", {}).get("end"),
        },
        "phase": _current_phase(protocol, calls, acceptance),
        "calls": calls,
        "quality": {
            "run_count": len(runs),
            "integrity_failures": integrity_failures,
            "api_errors": api_errors,
            "parse_failures": parse_failures,
        },
        "study0_acceptance": acceptance,
        "runs": runs,
        "warnings": warnings,
    }
