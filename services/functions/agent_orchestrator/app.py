"""Lambda handler for agent orchestration."""

from __future__ import annotations

from services.common.api import parse_body, response
from services.domain.agent_service import AgentService

SERVICE = AgentService()


def lambda_handler(event, _context):
    payload = parse_body(event)
    try:
        result = SERVICE.execute(payload)
        return response({"result": result})
    except ValueError as exc:
        return response({"error": str(exc)}, status_code=400)
