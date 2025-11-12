"""Lambda handler invoked by HTTP API or Step Functions to enqueue training."""

from __future__ import annotations

from services.common.api import parse_body, response
from services.domain.training_service import TrainingService

SERVICE = TrainingService()


def lambda_handler(event, _context):
    payload = parse_body(event)
    result = SERVICE.enqueue(payload)
    return response({"result": result}, status_code=202)
