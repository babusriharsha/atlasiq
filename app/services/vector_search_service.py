from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.embedding_service import generate_embedding


def search_similar_chunks(
    db: Session,
    query: str,
    team: str,
    limit: int = 5,
):
    query_embedding = generate_embedding(query)

    distance = Chunk.embedding.cosine_distance(query_embedding)

    return (
        db.query(
            Chunk,
            distance.label("distance"),
        )
        .join(Document, Chunk.document_id == Document.id)
        .filter(
            Chunk.embedding.is_not(None),
            Document.team == team,
        )
        .order_by(distance)
        .limit(limit)
        .all()
    )
