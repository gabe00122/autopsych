from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from .core import TrialSpec, utc_now
from .ledger import JsonlLedger
from .parsing import parse_response
from .providers import Provider


ScoreFunction = Callable[[TrialSpec, dict[str, Any]], dict[str, Any]]


def run_trials(
    run_id: str,
    trials: Iterable[TrialSpec],
    provider: Provider,
    ledger: JsonlLedger,
    scorer: ScoreFunction | None = None,
    max_attempts: int = 3,
) -> list[dict[str, Any]]:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    terminal_records: list[dict[str, Any]] = []
    for trial in trials:
        started_at = utc_now()
        response = None
        last_error: str | None = None
        attempts = 0
        for attempts in range(1, max_attempts + 1):
            try:
                response = provider.complete(trial)
                last_error = None
                break
            except Exception as error:  # provider errors must become data
                last_error = f"{type(error).__name__}: {error}"
        parsed = parse_response(response.content, trial.response_schema) if response else None
        scoring: dict[str, Any] = {}
        if parsed and parsed.status == "valid" and parsed.values is not None and scorer is not None:
            try:
                scoring = scorer(trial, parsed.values)
            except Exception as error:
                scoring = {"scoring_error": f"{type(error).__name__}: {error}"}
        record = {
            "schema_version": "1.0",
            "record_type": "trial_result",
            "run_id": run_id,
            "trial_id": trial.trial_id,
            "experiment_id": trial.experiment_id,
            "study": trial.study,
            "item_id": trial.item_id,
            "condition": trial.condition,
            "repetition": trial.repetition,
            "provider": trial.provider,
            "model_id": trial.model_id,
            "model_version": response.model_version if response else None,
            "started_at": started_at,
            "completed_at": utc_now(),
            "prompt_hash": trial.prompt_hash,
            "messages": list(trial.messages),
            "sampling": trial.sampling,
            "attempts": attempts,
            "api_status_code": response.status_code if response else None,
            "provider_request_id": response.request_id if response else None,
            "seed": response.seed if response else None,
            "system_fingerprint": response.system_fingerprint if response else None,
            "usage": response.usage if response else {},
            "raw_response": response.content if response else None,
            "parse_status": parsed.status if parsed else "api_error",
            "parse_errors": list(parsed.errors) if parsed else [],
            "recovered_json": parsed.recovered_json if parsed else False,
            "parsed_values": parsed.values if parsed else None,
            "scoring_results": scoring,
            "error": last_error,
            "metadata": trial.metadata,
        }
        ledger.append(record)
        terminal_records.append(record)
    return terminal_records
