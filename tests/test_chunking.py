from app.models.document import Document
from app.models.chunk import Chunk
from tests.conftest import TestingSessionLocal
from app.services.chunking_service import chunk_text


def test_chunk_text_with_overlap():
    text = "A" * 2500

    chunks = chunk_text(text)

    assert len(chunks) == 3
    assert len(chunks[0]) == 1000
    assert len(chunks[1]) == 1000
    assert len(chunks[2]) == 900


def test_chunk_text_empty():
    chunks = chunk_text("")

    assert chunks == []

def test_save_chunks():
    from app.services.chunking_service import save_chunks

    db = TestingSessionLocal()

    try:
        document = Document(
            filename="chunk_test.pdf",
            file_type="pdf",
            team="engineering",
            storage_path="/documents/chunk_test.pdf",
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        chunks = [
            "First chunk",
            "Second chunk",
        ]

        saved_chunks = save_chunks(
            db=db,
            document_id=document.id,
            chunks=chunks,
        )

        assert len(saved_chunks) == 2
        assert saved_chunks[0].chunk_index == 0
        assert saved_chunks[1].chunk_index == 1
        assert saved_chunks[0].content == "First chunk"
        assert saved_chunks[1].content == "Second chunk"
        assert saved_chunks[0].document_id == document.id

        stored_chunks = db.query(Chunk).all()

        assert len(stored_chunks) == 2

    finally:
        db.close()
