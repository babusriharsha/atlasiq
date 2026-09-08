from sqlalchemy.orm import Session

from app.services.keyword_search_service import search_keyword_chunks
from app.services.vector_search_service import search_similar_chunks


def hybrid_search(
    db: Session,
    query: str,
    team: str,
    limit: int = 5,
):
    vector_results = search_similar_chunks(
        db=db,
        query=query,
        team=team,
        limit=limit,
    )

    keyword_results = search_keyword_chunks(
        db=db,
        query=query,
        team=team,
        limit=limit,
    )

    combined = {}

    for rank, (chunk, distance) in enumerate(vector_results, start=1):
        combined[chunk.id] = {
            "chunk": chunk,
            "vector_rank": rank,
            "keyword_rank": None,
            "similarity": 1 - float(distance),
            "score": 1 / (60 + rank),
        }

    for rank, chunk in enumerate(keyword_results, start=1):
        keyword_score = 1 / (60 + rank)

        if chunk.id not in combined:
            combined[chunk.id] = {
                "chunk": chunk,
                "vector_rank": None,
                "keyword_rank": rank,
                "similarity": None,
                "score": keyword_score,
            }
        else:
            combined[chunk.id]["keyword_rank"] = rank
            combined[chunk.id]["score"] += keyword_score

    ranked_results = sorted(
        combined.values(),
        key=lambda result: result["score"],
        reverse=True,
    )

    return ranked_results[:limit]
