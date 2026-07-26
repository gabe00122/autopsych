from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


SEARCH_ENGINES = ("google", "bing")
FINAL_RATINGS = {"Low", "Medium", "High"}
COMPLETE_SEARCH_STATUSES = {"complete"}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: expected an object")
        records.append(value)
    return records


def stem_sha256(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def derive_contamination_rating(record: dict[str, Any]) -> str:
    searches = record.get("searches") or {}
    canonical = record.get("canonical_template_screen") or {}
    if any((searches.get(engine) or {}).get("status") not in COMPLETE_SEARCH_STATUSES for engine in SEARCH_ENGINES):
        return "Pending"
    if canonical.get("status") != "complete":
        return "Pending"
    if any(bool((searches.get(engine) or {}).get("top3_returns_same_numerical_answer")) for engine in SEARCH_ENGINES):
        return "High"
    if bool(canonical.get("canonical_match")):
        return "High"
    if any(bool((searches.get(engine) or {}).get("answer_feature_returns_estimate")) for engine in SEARCH_ENGINES):
        return "Medium"
    if canonical.get("template_overlap") == "substantial_noncanonical":
        return "Medium"
    return "Low"


def expected_disposition(rating: str) -> str:
    if rating == "High":
        return "exclude_or_redesign"
    if rating in {"Low", "Medium"}:
        return "retain_pending_other_reviews"
    return "do_not_select"


def audit_contamination_ledger(candidate_path: Path, ledger_path: Path) -> dict[str, Any]:
    candidates = _read_jsonl(candidate_path)
    ledger = _read_jsonl(ledger_path)
    errors: list[str] = []
    warnings: list[str] = []

    candidate_ids = [str(record.get("candidate_id") or "") for record in candidates]
    ledger_ids = [str(record.get("candidate_id") or "") for record in ledger]
    duplicate_candidates = sorted(key for key, count in Counter(candidate_ids).items() if count > 1)
    duplicate_ledger = sorted(key for key, count in Counter(ledger_ids).items() if count > 1)
    if duplicate_candidates:
        errors.append(f"duplicate candidate IDs: {duplicate_candidates}")
    if duplicate_ledger:
        errors.append(f"duplicate ledger IDs: {duplicate_ledger}")

    candidate_by_id = {str(record.get("candidate_id") or ""): record for record in candidates}
    ledger_by_id = {str(record.get("candidate_id") or ""): record for record in ledger}
    missing_ids = sorted(set(candidate_by_id) - set(ledger_by_id))
    unexpected_ids = sorted(set(ledger_by_id) - set(candidate_by_id))
    if missing_ids:
        errors.append(f"missing ledger records: {missing_ids}")
    if unexpected_ids:
        errors.append(f"unexpected ledger records: {unexpected_ids}")

    complete_by_engine = Counter({engine: 0 for engine in SEARCH_ENGINES})
    canonical_complete = 0
    ratings = Counter()
    dispositions = Counter()

    for candidate_id in sorted(set(candidate_by_id) & set(ledger_by_id)):
        candidate = candidate_by_id[candidate_id]
        record = ledger_by_id[candidate_id]
        prompt = candidate.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{candidate_id}: missing candidate prompt")
            continue
        expected_hash = stem_sha256(prompt)
        if record.get("stem_sha256") != expected_hash:
            errors.append(f"{candidate_id}: stem hash does not match candidate bank")

        searches = record.get("searches")
        if not isinstance(searches, dict):
            errors.append(f"{candidate_id}: missing searches object")
            searches = {}
        for engine in SEARCH_ENGINES:
            screen = searches.get(engine)
            if not isinstance(screen, dict):
                errors.append(f"{candidate_id}: missing {engine} screen")
                continue
            status = screen.get("status")
            if status in COMPLETE_SEARCH_STATUSES:
                complete_by_engine[engine] += 1
                if screen.get("query_type") != "exact_match_full_stem":
                    errors.append(f"{candidate_id}: {engine} query was not recorded as an exact full-stem search")
                if not screen.get("searched_on"):
                    errors.append(f"{candidate_id}: {engine} completion lacks a search date")
                if not isinstance(screen.get("top3_returns_same_numerical_answer"), bool):
                    errors.append(f"{candidate_id}: {engine} completion lacks a top-three answer judgment")
                if screen.get("evidence_quality") == "manual_summary_only":
                    warnings.append(f"{candidate_id}: {engine} has manual-summary evidence without captured top-three results")

        canonical = record.get("canonical_template_screen")
        if isinstance(canonical, dict) and canonical.get("status") == "complete":
            canonical_complete += 1
            if not isinstance(canonical.get("canonical_match"), bool):
                errors.append(f"{candidate_id}: canonical screen lacks a match judgment")
        else:
            canonical = {}

        derived_rating = derive_contamination_rating(record)
        recorded_rating = record.get("final_contamination_rating")
        ratings[str(recorded_rating or "Pending")] += 1
        if derived_rating != recorded_rating:
            errors.append(
                f"{candidate_id}: final rating {recorded_rating!r} does not match rubric-derived {derived_rating!r}"
            )
        recorded_disposition = record.get("disposition")
        dispositions[str(recorded_disposition or "missing")] += 1
        expected = expected_disposition(derived_rating)
        if recorded_disposition != expected:
            errors.append(
                f"{candidate_id}: disposition {recorded_disposition!r} does not match expected {expected!r}"
            )

    candidate_count = len(candidates)
    complete_ratings = sum(ratings[rating] for rating in FINAL_RATINGS)
    passes_acceptance = (
        not errors
        and len(ledger) == candidate_count
        and all(complete_by_engine[engine] == candidate_count for engine in SEARCH_ENGINES)
        and canonical_complete == candidate_count
        and complete_ratings == candidate_count
    )
    return {
        "candidate_count": candidate_count,
        "ledger_count": len(ledger),
        "complete_by_engine": dict(complete_by_engine),
        "canonical_complete": canonical_complete,
        "ratings": dict(ratings),
        "dispositions": dict(dispositions),
        "missing_ids": missing_ids,
        "unexpected_ids": unexpected_ids,
        "errors": errors,
        "warning_count": len(warnings),
        "warnings": warnings[:25],
        "warnings_truncated": len(warnings) > 25,
        "passes_acceptance": passes_acceptance,
    }
