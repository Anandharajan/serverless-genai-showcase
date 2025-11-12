"""Agent orchestration service (mock)."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List

from services.adapters import get_adapter
from services.data.store import AgentLifecycleStore, ModelMetadataStore
from services.observability.metrics import MetricsPublisher

logger = logging.getLogger(__name__)


class AgentService:
    def __init__(
        self,
        *,
        lifecycle_store: AgentLifecycleStore | None = None,
        metadata_store: ModelMetadataStore | None = None,
        metrics: MetricsPublisher | None = None,
    ):
        self._lifecycle = lifecycle_store or AgentLifecycleStore()
        self._metadata = metadata_store or ModelMetadataStore()
        self._metrics = metrics or MetricsPublisher()

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        goal = payload.get("goal", "").strip()
        if not goal:
            raise ValueError("goal is required")
        context = payload.get("context", {})

        model_id = payload.get("modelId") or self._metadata.get_active_model()
        adapter = get_adapter(model_id)
        plan = adapter.plan_agent(goal, context)
        plan_dict = {
            "steps": plan.steps,
            "rationale": plan.rationale,
            "estimatedCost": plan.estimated_cost,
        }
        run_record = self._lifecycle.start_run(plan=plan_dict)
        start = time.perf_counter()
        steps_result: List[Dict[str, Any]] = []
        for idx, step in enumerate(plan.steps, start=1):
            steps_result.append(
                {
                    "step": idx,
                    "action": step,
                    "status": "completed",
                    "details": f"Simulated execution for '{step}'",
                }
            )
        runtime_ms = (time.perf_counter() - start) * 1000
        result = {
            "runId": run_record["agentRunId"],
            "goal": goal,
            "steps": steps_result,
            "summary": f"Agent completed {len(plan.steps)} steps using {model_id}.",
        }
        self._lifecycle.complete_run(run_record["agentRunId"], result)
        self._metrics.publish_agent_runtime(run_record["agentRunId"], runtime_ms)
        logger.info("Agent run %s finished in %.2f ms", run_record["agentRunId"], runtime_ms)
        return result
