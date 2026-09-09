from sqlalchemy.orm import Session

from app.services.hybrid_search_service import hybrid_search


def evaluate_retrieval(
    db: Session,
    question: str,
    team: str,
    expected_document_id: int,
) -> dict:
    results = hybrid_search(
        db=db,
        query=question,
        team=team,
        limit=5,
    )

    retrieved_document_ids = [
        result["chunk"].document_id
        for result in results
    ]

    correct_document_retrieved = (
        expected_document_id in retrieved_document_ids
    )

    return {
        "question": question,
        "expected_document_id": expected_document_id,
        "retrieved_document_ids": retrieved_document_ids,
        "correct_document_retrieved": correct_document_retrieved,
    }
