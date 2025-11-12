"""Adapter registry returning the active provider implementation."""

from __future__ import annotations

import os
from typing import Dict

from .base import ModelAdapter
from .mock_adapter import MockModelAdapter

_ADAPTERS: Dict[str, ModelAdapter] = {}


def get_adapter(model_id: str | None = None) -> ModelAdapter:
    """
    Fetch (or lazily instantiate) the adapter for the supplied model ID.
    Falls back to the mock adapter when no provider is configured.
    """
    resolved_id = model_id or os.getenv("DEFAULT_MODEL_ID", "primary")
    adapter = _ADAPTERS.get(resolved_id)
    if adapter:
        return adapter
    provider = os.getenv("MODEL_PROVIDER", "mock").lower()
    if provider == "mock":
        adapter = MockModelAdapter(model_id=resolved_id)
    else:
        raise RuntimeError(
            f"Provider '{provider}' not implemented in this sample. "
            "Add your adapter under services/adapters."
        )
    _ADAPTERS[resolved_id] = adapter
    return adapter
