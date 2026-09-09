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
def evaluate_retrieval_dataset(
    db: Session,
    evaluation_cases: list[dict],
) -> dict:
    results = []

    for case in evaluation_cases:
        result = evaluate_retrieval(
            db=db,
            question=case["question"],
            team=case["team"],
            expected_document_id=case["expected_document_id"],
        )

        results.append(result)

    total_cases = len(results)

    correct_cases = sum(
        1
        for result in results
        if result["correct_document_retrieved"]
    )

    accuracy = (
        round((correct_cases / total_cases) * 100, 2)
        if total_cases > 0
        else 0.0
    )

    return {
        "total_cases": total_cases,
        "correct_cases": correct_cases,
        "incorrect_cases": total_cases - correct_cases,
        "retrieval_accuracy_percent": accuracy,
        "results": results,
    }
