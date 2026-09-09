from app.services.evaluation_service import (
    evaluate_retrieval,
    evaluate_retrieval_dataset,
)
from app.models.document import Document
from app.services.chunking_service import save_chunks
from app.services.evaluation_service import evaluate_retrieval
from tests.conftest import TestingSessionLocal


def test_retrieval_evaluation_finds_expected_document():
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

        result = evaluate_retrieval(
            db=db,
            question="Who approves refunds above $500?",
            team="engineering",
            expected_document_id=document.id,
        )

        assert result["correct_document_retrieved"] is True
        assert document.id in result["retrieved_document_ids"]

    finally:
        db.close()
def test_retrieval_dataset_accuracy():
    db = TestingSessionLocal()

    try:
        refund_document = Document(
            filename="refund_policy.txt",
            file_type="txt",
            team="engineering",
            storage_path="refund_policy.txt",
        )

        deployment_document = Document(
            filename="deployment_guide.txt",
            file_type="txt",
            team="engineering",
            storage_path="deployment_guide.txt",
        )

        db.add_all([
            refund_document,
            deployment_document,
        ])

        db.commit()

        db.refresh(refund_document)
        db.refresh(deployment_document)

        save_chunks(
            db=db,
            document_id=refund_document.id,
            chunks=[
                "Refunds above $500 require manager approval."
            ],
        )

        save_chunks(
            db=db,
            document_id=deployment_document.id,
            chunks=[
                "Production releases require approval from the engineering lead."
            ],
        )

        evaluation_cases = [
            {
                "question": "Who approves refunds above $500?",
                "team": "engineering",
                "expected_document_id": refund_document.id,
            },
            {
                "question": "Who approves production releases?",
                "team": "engineering",
                "expected_document_id": deployment_document.id,
            },
        ]

        result = evaluate_retrieval_dataset(
            db=db,
            evaluation_cases=evaluation_cases,
        )

        assert result["total_cases"] == 2
        assert result["correct_cases"] == 2
        assert result["incorrect_cases"] == 0
        assert result["retrieval_accuracy_percent"] == 100.0

    finally:
        db.close()
