"""Fine-tune and evaluation pipeline stub."""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict

from services.adapters import get_adapter
from services.data.store import ModelMetadataStore


class TrainingService:
    def __init__(self, *, metadata_store: ModelMetadataStore | None = None):
        self._metadata = metadata_store or ModelMetadataStore()

    def enqueue(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        model_id = payload.get("modelId") or self._metadata.get_active_model()
        adapter = get_adapter(model_id)
        result = adapter.training_hook(payload)
        return {
            "modelId": model_id,
            "status": result.get("status", "accepted"),
            "jobId": result.get("jobId"),
            "receivedAt": dt.datetime.utcnow().isoformat() + "Z",
        }
