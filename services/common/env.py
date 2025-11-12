"""Environment helpers."""

from __future__ import annotations

import os


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name)
    if value is None:
        if default is None:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return default
    return value


PROMPT_TABLE = "genai-prompt-dev" if "LOCALSTACK_EDGE_PORT" in os.environ else get_env("PROMPT_TABLE", "local-PromptHistory")
MODEL_TABLE = "genai-model-dev" if "LOCALSTACK_EDGE_PORT" in os.environ else get_env("MODEL_TABLE", "local-ModelMetadata")
AGENT_TABLE = "genai-agent-dev" if "LOCALSTACK_EDGE_PORT" in os.environ else get_env("AGENT_TABLE", "local-AgentLifecycle")
RETRIEVAL_TABLE = "genai-retrieval-dev" if "LOCALSTACK_EDGE_PORT" in os.environ else get_env("RETRIEVAL_TABLE", "local-RetrievalIndex")
DEFAULT_MODEL_ID = get_env("DEFAULT_MODEL_ID", "primary")
STAGE = get_env("STAGE", "dev")
# Local directory for fallbacks when DynamoDB is unavailable.
LOCAL_STATE_DIR = os.getenv("GENAI_STATE_DIR", os.path.join("/tmp", "genai-showcase"))
