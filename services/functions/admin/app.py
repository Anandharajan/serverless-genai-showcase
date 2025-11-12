"""Lambda handler for model administration."""

from __future__ import annotations

from services.common.api import parse_body, response
from services.domain.admin_service import AdminService

SERVICE = AdminService()


def lambda_handler(event, _context):
    payload = parse_body(event)
    try:
        result = SERVICE.handle(payload)
        return response({"result": result})
    except ValueError as exc:
        return response({"error": str(exc)}, status_code=400)
