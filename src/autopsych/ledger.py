from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .core import TrialSpec, sha256_json, utc_now


def write_manifest(
    path: Path,
    run_id: str,
    trials: Iterable[TrialSpec],
    protocol_id: str,
    preregistration_url: str | None = None,
) -> dict[str, Any]:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite immutable manifest: {path}")
    serialized = [trial.to_dict() for trial in trials]
    manifest = {
        "schema_version": "1.0",
        "run_id": run_id,
        "protocol_id": protocol_id,
        "preregistration_url": preregistration_url,
        "created_at": utc_now(),
        "intended_trial_count": len(serialized),
        "intended_trial_ids": [trial["trial_id"] for trial in serialized],
        "trials_sha256": sha256_json(serialized),
        "trials": serialized,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


class JsonlLedger:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            records.append(value)
    return records
