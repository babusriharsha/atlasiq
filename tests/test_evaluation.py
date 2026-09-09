from app.models.document import Document
from app.services.chunking_service import save_chunks
from app.services.evaluation_service import evaluate_retrieval
from tests.conftest import TestingSessionLocal


def test_retrieval_evaluation_finds_expected_document():
    db = TestingSessionLocal()

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

        result = evaluate_retrieval(
            db=db,
            question="Who approves refunds above $500?",
            team="engineering",
            expected_document_id=document.id,
        )

        assert result["correct_document_retrieved"] is True
        assert document.id in result["retrieved_document_ids"]

    finally:
        db.close()
