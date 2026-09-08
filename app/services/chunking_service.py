from sqlalchemy.orm import Session
from app.models.chunk import Chunk
from app.services.embedding_service import generate_embedding

def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:
    if not text.strip():
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start += chunk_size - overlap

    return chunks

def save_chunks(
    db: Session,
    document_id: int,
    chunks: list[str],
) -> list[Chunk]:
    saved_chunks = []

    for index, content in enumerate(chunks):
        chunk = Chunk(
            document_id=document_id,
            chunk_index=index,
            content=content,
            embedding=generate_embedding(content),
        )

        db.add(chunk)
        saved_chunks.append(chunk)

    db.commit()

    for chunk in saved_chunks:
        db.refresh(chunk)

    return saved_chunks
