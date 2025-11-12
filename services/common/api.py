"""Helper utilities for API Gateway Lambda proxies."""

from __future__ import annotations

import json
from typing import Any, Dict


def parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """Parse JSON body from an API Gateway event with safe fallback."""
    body = event.get("body") or "{}"
    if isinstance(body, (dict, list)):
        return body if isinstance(body, dict) else {"payload": body}
    try:
        return json.loads(body)
    except (TypeError, json.JSONDecodeError):
        return {}


def response(payload: Dict[str, Any], status_code: int = 200) -> Dict[str, Any]:
    """Create a standard HTTP JSON response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(payload),
    }
