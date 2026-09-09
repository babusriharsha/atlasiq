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
def test_hybrid_search_merges_vector_and_keyword_results(monkeypatch):
    class FakeChunk:
        def __init__(self, chunk_id):
            self.id = chunk_id

    chunk = FakeChunk(1)

    monkeypatch.setattr(
        "app.services.hybrid_search_service.search_similar_chunks",
        lambda **kwargs: [(chunk, 0.2)],
    )

    monkeypatch.setattr(
        "app.services.hybrid_search_service.search_keyword_chunks",
        lambda **kwargs: [chunk],
    )

    results = hybrid_search(
        db=None,
        query="refund policy",
        team="engineering",
        limit=5,
    )

    assert len(results) == 1
    assert results[0]["vector_rank"] == 1
    assert results[0]["keyword_rank"] == 1
    assert results[0]["score"] == (1 / 61) + (1 / 61)


def test_hybrid_search_includes_keyword_only_result(monkeypatch):
    class FakeChunk:
        def __init__(self, chunk_id):
            self.id = chunk_id

    vector_chunk = FakeChunk(1)
    keyword_chunk = FakeChunk(2)

    monkeypatch.setattr(
        "app.services.hybrid_search_service.search_similar_chunks",
        lambda **kwargs: [(vector_chunk, 0.2)],
    )

    monkeypatch.setattr(
        "app.services.hybrid_search_service.search_keyword_chunks",
        lambda **kwargs: [keyword_chunk],
    )

    results = hybrid_search(
        db=None,
        query="refund policy",
        team="engineering",
        limit=5,
    )

    result_by_id = {
        result["chunk"].id: result
        for result in results
    }

    assert result_by_id[2]["vector_rank"] is None
    assert result_by_id[2]["keyword_rank"] == 1
    assert result_by_id[2]["similarity"] is None
