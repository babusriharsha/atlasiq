from app.models.document import Document
from app.services.chunking_service import save_chunks
from app.services.vector_search_service import search_similar_chunks
from tests.conftest import TestingSessionLocal


def test_vector_search_respects_team_access():
    db = TestingSessionLocal()

    try:
        engineering_doc = Document(
            filename="engineering.txt",
            file_type="txt",
            team="engineering",
            storage_path="engineering.txt",
        )

        db.add(engineering_doc)
        db.commit()
        db.refresh(engineering_doc)

        save_chunks(
            db=db,
            document_id=engineering_doc.id,
            chunks=["Refunds above $500 require manager approval."],
        )

        results = search_similar_chunks(
            db=db,
            query="Who approves large refunds?",
            team="customer_support",
            limit=5,
        )

        assert results == []
    finally:
        db.close()
