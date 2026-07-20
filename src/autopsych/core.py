from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class TrialSpec:
    experiment_id: str
    study: str
    item_id: str
    condition: str
    repetition: int
    provider: str
    model_id: str
    messages: tuple[dict[str, str], ...]
    response_schema: dict[str, Any]
    sampling: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def prompt_hash(self) -> str:
        return sha256_json(list(self.messages))

    @property
    def trial_id(self) -> str:
        identity = {
            "experiment_id": self.experiment_id,
            "study": self.study,
            "item_id": self.item_id,
            "condition": self.condition,
            "repetition": self.repetition,
            "provider": self.provider,
            "model_id": self.model_id,
            "prompt_hash": self.prompt_hash,
            "sampling": self.sampling,
        }
        return sha256_json(identity)[:24]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["messages"] = list(self.messages)
        value["trial_id"] = self.trial_id
        value["prompt_hash"] = self.prompt_hash
        return value


@dataclass(frozen=True)
class ProviderResponse:
    content: str
    model_version: str | None = None
    status_code: int | None = None
    request_id: str | None = None
    seed: int | None = None
    system_fingerprint: str | None = None
    usage: dict[str, Any] = field(default_factory=dict)
