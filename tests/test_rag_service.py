from app.models.document import Document
from app.services.chunking_service import save_chunks
from app.services.rag_service import answer_question, NO_DOCUMENTATION_MESSAGE
from tests.conftest import TestingSessionLocal


def test_rag_returns_grounded_answer(monkeypatch):
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
            chunks=[
                "Refunds above $500 require manager approval."
            ],
        )

        result = answer_question(
            db=db,
            question="Who approves refunds above $500?",
            team="engineering",
        )

        assert "manager" in result["answer"].lower()
        assert len(result["sources"]) > 0
        assert result["sources"][0]["document_id"] == document.id

    finally:
        db.close()


def test_rag_returns_no_documentation():
    db = TestingSessionLocal()

    try:
        result = answer_question(
            db=db,
            question="What is the company vacation policy?",
            team="engineering",
        )

        assert result["answer"] == NO_DOCUMENTATION_MESSAGE
        assert result["sources"] == []

    finally:
        db.close()
