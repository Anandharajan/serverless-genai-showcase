"""
Adapter interfaces that hide the underlying model provider.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence


@dataclass
class GenerationRequest:
    prompt: str
    system: str | None = None
    max_tokens: int = 256
    temperature: float = 0.2
    mode: str = "completion"  # completion | summarize
    metadata: dict = field(default_factory=dict)


@dataclass
class GenerationResponse:
    text: str
    tokens_used: int
    model_id: str
    metadata: dict = field(default_factory=dict)


@dataclass
class RagRequest:
    question: str
    documents: Sequence[dict]
    model_id: str
    top_k: int = 4
    metadata: dict = field(default_factory=dict)


@dataclass
class RagResponse:
    answer: str
    contexts: List[dict]
    tokens_used: int
    model_id: str


@dataclass
class AgentPlan:
    steps: List[str]
    rationale: str
    estimated_cost: float


class ModelAdapter:
    """Base adapter with sensible fallbacks for the sample project."""

    def __init__(self, model_id: str):
        self.model_id = model_id

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        raise NotImplementedError

    def rag(self, request: RagRequest) -> RagResponse:
        raise NotImplementedError

    def plan_agent(self, goal: str, context: dict | None = None) -> AgentPlan:
        raise NotImplementedError

    def summarize(self, text: str, max_tokens: int = 128) -> GenerationResponse:
        raise NotImplementedError

    def training_hook(self, payload: dict) -> dict:
        """Optional hook invoked by the trainer Lambda/Step Function."""
        return {
            "status": "accepted",
            "model_id": self.model_id,
            "payload": payload,
        }
