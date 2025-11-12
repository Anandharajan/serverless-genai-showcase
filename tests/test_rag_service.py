from services.domain.rag_service import RagService


def test_rag_returns_contexts():
    service = RagService()
    payload = {
        "question": "What does the showcase demonstrate?",
        "documents": [
            {"docId": "1", "content": "The showcase demonstrates adapters and observability."},
            {"docId": "2", "content": "It also includes governance documents."},
        ],
    }
    response = service.answer(payload)
    assert response["contexts"]
    assert "adapters" in response["answer"]
