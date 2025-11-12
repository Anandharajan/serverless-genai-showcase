"""Model registry administration service."""

from __future__ import annotations

from typing import Any, Dict

from services.data.store import ModelMetadataStore


class AdminService:
    def __init__(self, *, metadata_store: ModelMetadataStore | None = None):
        self._metadata = metadata_store or ModelMetadataStore()

    def handle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = (payload.get("action") or "list").lower()
        if action == "register":
            model = self._metadata.register_model(payload)
            should_activate = payload.get("activate")
            if should_activate is None:
                should_activate = payload.get("makeActive")
            if should_activate is None:
                should_activate = True
            if should_activate:
                model = self._metadata.set_active(model["modelId"])
                message = "model registered and activated"
            else:
                message = "model registered"
            return {"message": message, "model": model}
        if action == "activate":
            model_id = payload.get("modelId")
            if not model_id:
                raise ValueError("modelId is required to activate a model")
            model = self._metadata.set_active(model_id)
            return {"message": f"{model_id} activated", "model": model}
        if action == "active":
            return {"modelId": self._metadata.get_active_model()}
        return {"models": self._metadata.list_models()}
