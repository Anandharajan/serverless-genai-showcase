
import pytest


@pytest.fixture(autouse=True)
def configure_local_env(tmp_path, monkeypatch):
    """Force the services to use local JSON state during tests."""
    monkeypatch.setenv("GENAI_LOCAL_ONLY", "1")
    monkeypatch.setenv("GENAI_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("PROMPT_TABLE", "test-prompt")
    monkeypatch.setenv("MODEL_TABLE", "test-model")
    monkeypatch.setenv("AGENT_TABLE", "test-agent")
    monkeypatch.setenv("RETRIEVAL_TABLE", "test-retrieval")
    monkeypatch.setenv("DEFAULT_MODEL_ID", "primary")
    yield
