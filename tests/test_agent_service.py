from services.domain.agent_service import AgentService


def test_agent_execution_returns_steps():
    service = AgentService()
    payload = {
        "goal": "Summarize system metrics",
        "context": {"dataset": "cloudwatch"},
    }
    result = service.execute(payload)
    assert result["steps"]
    assert result["runId"]
