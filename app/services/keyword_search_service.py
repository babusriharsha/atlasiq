from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document


def search_keyword_chunks(
    db: Session,
    query: str,
    team: str,
    limit: int = 5,
):
    return (
        db.query(Chunk)
        .join(Document, Chunk.document_id == Document.id)
        .filter(
            Document.team == team,
            Chunk.content.ilike(f"%{query}%"),
        )
        .limit(limit)
        .all()
    )
