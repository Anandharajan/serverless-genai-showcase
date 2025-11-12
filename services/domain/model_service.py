"""Domain logic for text generation and summarization."""

from __future__ import annotations

import logging
from typing import Any, Dict

from services.adapters import get_adapter
from services.adapters.base import GenerationRequest
from services.data.store import ModelMetadataStore, PromptHistoryStore
from services.observability.metrics import MetricsPublisher

logger = logging.getLogger(__name__)


class ModelService:
    def __init__(
        self,
        *,
        adapter_factory=get_adapter,
        prompt_store: PromptHistoryStore | None = None,
        metadata_store: ModelMetadataStore | None = None,
        metrics: MetricsPublisher | None = None,
    ):
        self._adapter_factory = adapter_factory
        self._prompts = prompt_store or PromptHistoryStore()
        self._metadata = metadata_store or ModelMetadataStore()
        self._metrics = metrics or MetricsPublisher()

    def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        prompt = payload.get("prompt", "").strip()
        if not prompt:
            raise ValueError("Prompt is required.")

        mode = payload.get("mode", payload.get("action", "completion"))
        model_id = payload.get("modelId") or self._metadata.get_active_model()
        adapter = self._adapter_factory(model_id)
        request = GenerationRequest(
            prompt=prompt,
            system=payload.get("system"),
            max_tokens=int(payload.get("maxTokens", 256)),
            temperature=float(payload.get("temperature", 0.25)),
            mode=mode,
            metadata={"stage": payload.get("stage", "dev")},
        )

        if mode == "summarize":
            result = adapter.summarize(prompt, max_tokens=request.max_tokens)
        else:
            result = adapter.generate(request)

        user_id = payload.get("userId", "anonymous")
        record = self._prompts.log_prompt(
            user_id=user_id, prompt=prompt, response=result.text, model_id=result.model_id
        )
        self._metrics.publish_token_usage(result.model_id, result.tokens_used)
        logger.info("Generated text using model %s for user %s", model_id, user_id)

        return {
            "output": result.text,
            "tokensUsed": result.tokens_used,
            "modelId": result.model_id,
            "promptId": record["requestId"],
            "metadata": result.metadata,
        }
