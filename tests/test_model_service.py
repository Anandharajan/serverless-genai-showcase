from services.domain.model_service import ModelService


def test_generate_completion_logs_prompt(tmp_path, monkeypatch):
    service = ModelService()
    payload = {
        "prompt": "Explain why observability matters.",
        "userId": "tester",
        "mode": "completion",
    }
    result = service.generate(payload)
    assert "output" in result
    assert result["modelId"]
    assert result["tokensUsed"] > 0


def test_generate_summary_mode():
    service = ModelService()
    payload = {
        "prompt": "First sentence. Second sentence. Third.",
        "mode": "summarize",
    }
    result = service.generate(payload)
    assert "First sentence" in result["output"]
