"""Lambda handler for retrieval augmented generation queries."""

from __future__ import annotations

from services.common.api import parse_body, response
from services.domain.rag_service import RagService

SERVICE = RagService()


def lambda_handler(event, _context):
    payload = parse_body(event)
    try:
        result = SERVICE.answer(payload)
        return response({"result": result})
    except ValueError as exc:
        return response({"error": str(exc)}, status_code=400)
