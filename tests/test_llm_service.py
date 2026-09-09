from app.services.llm_service import MODEL_NAME, generate_answer


def test_generate_answer_calls_ollama(monkeypatch):
    captured = {}

    def fake_chat(model, messages):
        captured["model"] = model
        captured["messages"] = messages

        return {
            "message": {
                "content": "Manager approval is required."
            }
        }

    monkeypatch.setattr(
        "app.services.llm_service.ollama.chat",
        fake_chat,
    )

    answer = generate_answer("Who approves refunds?")

    assert answer == "Manager approval is required."
    assert captured["model"] == MODEL_NAME
    assert captured["messages"] == [
        {
            "role": "user",
            "content": "Who approves refunds?",
        }
    ]
