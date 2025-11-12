"""Minimal CloudWatch metrics publisher with local logging fallback."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)

try:
    import boto3  # type: ignore

except Exception:  # pragma: no cover
    boto3 = None


class MetricsPublisher:
    def __init__(self, namespace: str = "GenAI/Usage"):
        self.namespace = namespace
        self._client = None
        if os.getenv("GENAI_LOCAL_ONLY") != "1" and boto3 is not None:
            try:
                self._client = boto3.client("cloudwatch")
            except Exception:
                self._client = None

    def publish(
        self,
        metric_name: str,
        value: float,
        unit: str = "Count",
        dimensions: Dict[str, str] | None = None,
    ) -> None:
        datum = {
            "MetricName": metric_name,
            "Value": value,
            "Unit": unit,
            "Timestamp": datetime.utcnow(),
            "Dimensions": [{"Name": k, "Value": v} for k, v in (dimensions or {}).items()],
        }
        if self._client:
            try:
                self._client.put_metric_data(Namespace=self.namespace, MetricData=[datum])
                return
            except Exception as exc:  # pragma: no cover
                logger.warning("Failed to publish metric %s: %s", metric_name, exc)
        logger.info("[Metric:%s] %s", metric_name, json.dumps(datum, default=str))

    def publish_token_usage(self, model_id: str, tokens: int) -> None:
        self.publish(
            metric_name="TokenUsageByModel",
            value=tokens,
            unit="Count",
            dimensions={"ModelId": model_id},
        )

    def publish_agent_runtime(self, run_id: str, milliseconds: float) -> None:
        self.publish(
            metric_name="AgentRuntimeMs",
            value=milliseconds,
            unit="Milliseconds",
            dimensions={"AgentRunId": run_id},
        )
