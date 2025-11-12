"""Deterministic adapter so the sample can run without external APIs."""

from __future__ import annotations

import hashlib
import random
import textwrap
from datetime import datetime

from .base import (
    AgentPlan,
    GenerationRequest,
    GenerationResponse,
    ModelAdapter,
    RagRequest,
    RagResponse,
)


class MockModelAdapter(ModelAdapter):
    """
    Handy adapter that produces explainable text using only stdlib
    operations. This keeps the repo dependency-light while exposing the
    seams needed to plug real providers.
    """

    def __init__(self, model_id: str):
        super().__init__(model_id=model_id)
        random.seed(hash(model_id) & 0xFFFF)

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        prompt = request.prompt.strip()
        if not prompt:
            prompt = "No prompt provided."
        if request.mode == "summarize":
            text = self._summarize(prompt, request.max_tokens)
        else:
            text = self._reflect(prompt, request.max_tokens, request.temperature)
        tokens = max(12, min(len(text.split()), request.max_tokens))
        return GenerationResponse(
            text=text,
            tokens_used=tokens,
            model_id=self.model_id,
            metadata={
                "mode": request.mode,
                "echo": prompt[:80],
                "created": datetime.utcnow().isoformat() + "Z",
            },
        )

    def summarize(self, text: str, max_tokens: int = 128) -> GenerationResponse:
        summary = self._summarize(text, max_tokens)
        tokens = min(len(summary.split()), max_tokens)
        return GenerationResponse(
            text=summary,
            tokens_used=tokens,
            model_id=self.model_id,
            metadata={"mode": "summarize"},
        )

    def rag(self, request: RagRequest) -> RagResponse:
        docs = list(request.documents)[: request.top_k]
        contexts = []
        aggregate = []
        for doc in docs:
            snippet = doc.get("content", "")[:320]
            score = self._score_similarity(request.question, snippet)
            contexts.append(
                {
                    "docId": doc.get("docId") or self._hash(snippet),
                    "score": round(score, 3),
                    "metadata": doc.get("metadata", {}),
                    "excerpt": snippet,
                }
            )
            aggregate.append(f"[{score:.2f}] {snippet}")
        answer = textwrap.dedent(
            f"""
            Based on {len(contexts)} context documents I found the following insight:
            {self._reflect(request.question + " " + " ".join(aggregate), 240, 0.15)}
            """
        ).strip()
        tokens = max(24, min(len(answer.split()), 256))
        return RagResponse(
            answer=answer,
            contexts=contexts,
            tokens_used=tokens,
            model_id=self.model_id,
        )

    def plan_agent(self, goal: str, context: dict | None = None) -> AgentPlan:
        context = context or {}
        deterministic = self._hash(goal + str(sorted(context.items())))
        estimated_cost = (int(deterministic[:4], 16) % 1000) / 100.0
        steps = [
            f"Clarify goal: {goal}",
            f"Collect context: {', '.join(context.keys()) or 'none'}",
            "Execute reasoning loop",
            "Aggregate findings and produce answer",
        ]
        rationale = (
            "Generated deterministically by MockModelAdapter to ensure the "
            "agent pipeline stays testable without external models."
        )
        return AgentPlan(steps=steps, rationale=rationale, estimated_cost=estimated_cost)

    def training_hook(self, payload: dict) -> dict:
        return {
            "status": "accepted",
            "jobId": self._hash(str(payload)),
            "model_id": self.model_id,
            "received": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def _reflect(prompt: str, max_tokens: int, temperature: float) -> str:
        influence = 1 + int(temperature * 10)
        reversed_prompt = " ".join(reversed(prompt.split()))
        text = f"{prompt} | Reflection:{reversed_prompt[: max_tokens * influence // 4]}"
        return text[: max_tokens * 8]

    @staticmethod
    def _summarize(text: str, max_tokens: int) -> str:
        sentences = [segment.strip() for segment in text.split(".") if segment.strip()]
        if not sentences:
            return text[: max_tokens * 4]
        summary = " ".join(sentences[:2])
        return summary[: max_tokens * 4]

    @staticmethod
    def _score_similarity(question: str, content: str) -> float:
        if not content:
            return 0.0
        overlap = len(set(question.lower().split()) & set(content.lower().split()))
        return min(1.0, overlap / max(1, len(question.split())))

    @staticmethod
    def _hash(value: str) -> str:
        return hashlib.sha1(value.encode("utf-8")).hexdigest()
