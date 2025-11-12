"""Lambda handler for text generation & summarization."""

from __future__ import annotations

from services.common.api import parse_body, response
from services.domain.model_service import ModelService

SERVICE = ModelService()


def lambda_handler(event, _context):
    payload = parse_body(event)
    try:
        result = SERVICE.generate(payload)
        return response({"result": result})
    except ValueError as exc:
        return response({"error": str(exc)}, status_code=400)
