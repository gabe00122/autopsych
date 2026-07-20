from __future__ import annotations

import os
from typing import Protocol

from .core import ProviderResponse, TrialSpec


class Provider(Protocol):
    def complete(self, trial: TrialSpec) -> ProviderResponse: ...


class SequenceProvider:
    """Deterministic provider for unit tests and dry runs."""

    def __init__(self, responses: list[ProviderResponse]):
        self.responses = iter(responses)

    def complete(self, trial: TrialSpec) -> ProviderResponse:
        return next(self.responses)


class OpenRouterProvider:
    """Development adapter. Confirmatory routes must follow the frozen provider policy."""

    def __init__(self, api_key: str | None = None):
        from openrouter import OpenRouter

        key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise RuntimeError("OPENROUTER_API_KEY is required")
        self.client = OpenRouter(api_key=key)

    def complete(self, trial: TrialSpec) -> ProviderResponse:
        kwargs = dict(trial.sampling)
        response = self.client.chat.send(
            model=trial.model_id,
            messages=list(trial.messages),
            **kwargs,
        )
        content = response.choices[0].message.content
        usage = getattr(response, "usage", None)
        usage_dict = usage.model_dump() if hasattr(usage, "model_dump") else {}
        return ProviderResponse(
            content=content,
            model_version=getattr(response, "model", None),
            request_id=getattr(response, "id", None),
            usage=usage_dict,
        )
