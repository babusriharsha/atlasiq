from app.models.document import Document
from app.services.chunking_service import save_chunks
from app.services.hybrid_search_service import hybrid_search
from tests.conftest import TestingSessionLocal


def test_hybrid_search_returns_relevant_result():
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

        results = hybrid_search(
            db=db,
            query="Who approves a large refund?",
            team="engineering",
            limit=5,
        )

        assert len(results) > 0
        assert results[0]["chunk"].document_id == document.id

    finally:
        db.close()
