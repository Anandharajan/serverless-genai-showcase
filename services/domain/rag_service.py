"""RAG domain logic."""

from __future__ import annotations

import logging
from typing import Any, Dict, Sequence

from services.adapters import get_adapter
from services.adapters.base import RagRequest
from services.data.store import ModelMetadataStore, PromptHistoryStore, RetrievalIndexStore
from services.observability.metrics import MetricsPublisher

logger = logging.getLogger(__name__)


class RagService:
    def __init__(
        self,
        *,
        metadata_store: ModelMetadataStore | None = None,
        prompt_store: PromptHistoryStore | None = None,
        retrieval_store: RetrievalIndexStore | None = None,
        metrics: MetricsPublisher | None = None,
    ):
        self._metadata = metadata_store or ModelMetadataStore()
        self._prompts = prompt_store or PromptHistoryStore()
        self._retrieval = retrieval_store or RetrievalIndexStore()
        self._metrics = metrics or MetricsPublisher()

    def answer(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        question = payload.get("question", "").strip()
        if not question:
            raise ValueError("question is required")

        documents: Sequence[Dict[str, Any]] = payload.get("documents") or self._retrieval.top_k(
            int(payload.get("topK", 4))
        )
        model_id = payload.get("modelId") or self._metadata.get_active_model()
        adapter = get_adapter(model_id)
        rag_request = RagRequest(
            question=question,
            documents=documents,
            model_id=model_id,
            top_k=int(payload.get("topK", 4)),
            metadata={"tenant": payload.get("tenant", "default")},
        )
        result = adapter.rag(rag_request)
        self._prompts.log_prompt(
            user_id=payload.get("userId", "anonymous"),
            prompt=question,
            response=result.answer,
            model_id=model_id,
        )
        self._metrics.publish_token_usage(model_id, result.tokens_used)
        logger.info("Generated RAG answer using model %s", model_id)
        return {
            "answer": result.answer,
            "contexts": result.contexts,
            "modelId": model_id,
            "tokensUsed": result.tokens_used,
        }
