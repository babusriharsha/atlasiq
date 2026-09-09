from app.models.document import Document
from app.services.chunking_service import save_chunks
from tests.conftest import TestingSessionLocal, client
from app.models.query_log import QueryLog
from tests.conftest import TestingSessionLocal

def test_ask_endpoint_returns_grounded_answer(monkeypatch):
    db = TestingSessionLocal()

    monkeypatch.setattr(
        "app.services.rag_service.generate_answer",
        lambda prompt: "Manager approval is required for refunds above $500.",
    )

    try:
        document = Document(
            filename="refund_policy.txt",
            file_type="txt",
            team="engineering",
            storage_path="refund_policy.txt",
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        save_chunks(
            db=db,
            document_id=document.id,
            chunks=["Refunds above $500 require manager approval."],
        )

        response = client.post(
            "/ask",
            json={
                "question": "Who approves refunds above $500?",
                "team": "engineering",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert "manager" in data["answer"].lower()
        assert data["sources"][0]["document_id"] == document.id

    finally:
        db.close()
def test_ask_creates_query_log(monkeypatch):
    monkeypatch.setattr(
        "app.services.rag_service.generate_answer",
        lambda prompt: "Manager approval is required.",
    )

    db = TestingSessionLocal()

    document = Document(
        filename="refund_policy.txt",
        file_type="txt",
        team="engineering",
        storage_path="refund_policy.txt",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    save_chunks(
        db=db,
        document_id=document.id,
        chunks=[
            "Refunds above $500 require manager approval."
        ],
    )

    db.close()

    response = client.post(
        "/ask",
        json={
            "question": "Who approves refunds above $500?",
            "team": "engineering",
        },
    )

    assert response.status_code == 200

    db = TestingSessionLocal()

    try:
        query_log = db.query(QueryLog).first()

        assert query_log is not None
        assert query_log.team == "engineering"
        assert query_log.model_name == "llama3.2:3b"
        assert query_log.latency_seconds >= 0
        assert query_log.estimated_cost_usd == 0.0

    finally:
        db.close()
