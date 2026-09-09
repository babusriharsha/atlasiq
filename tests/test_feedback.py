from tests.conftest import client


def test_create_feedback():
    response = client.post(
        "/feedback",
        json={
            "question": "Who approves refunds above $500?",
            "answer": "Manager approval is required.",
            "team": "engineering",
            "rating": "correct",
            "correction": None,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["question"] == "Who approves refunds above $500?"
    assert data["rating"] == "correct"
    assert data["team"] == "engineering"


def test_feedback_rejects_invalid_rating():
    response = client.post(
        "/feedback",
        json={
            "question": "Test question",
            "answer": "Test answer",
            "team": "engineering",
            "rating": "maybe",
            "correction": None,
        },
    )

    assert response.status_code == 422
