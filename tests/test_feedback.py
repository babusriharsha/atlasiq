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
def test_feedback_metrics():
    client.post(
        "/feedback",
        json={
            "question": "Question 1",
            "answer": "Answer 1",
            "team": "engineering",
            "rating": "correct",
            "correction": None,
        },
    )

    client.post(
        "/feedback",
        json={
            "question": "Question 2",
            "answer": "Answer 2",
            "team": "engineering",
            "rating": "incorrect",
            "correction": "Corrected answer",
        },
    )

    response = client.get("/metrics/feedback")

    assert response.status_code == 200

    data = response.json()

    assert data["total_feedback"] == 2
    assert data["correct"] == 1
    assert data["incorrect"] == 1
    assert data["accuracy_percent"] == 50.0


def test_feedback_metrics_by_team():
    client.post(
        "/feedback",
        json={
            "question": "Engineering question",
            "answer": "Engineering answer",
            "team": "engineering",
            "rating": "correct",
            "correction": None,
        },
    )

    client.post(
        "/feedback",
        json={
            "question": "Support question",
            "answer": "Support answer",
            "team": "customer_support",
            "rating": "incorrect",
            "correction": "Correct support answer",
        },
    )

    response = client.get(
        "/metrics/feedback?team=engineering"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_feedback"] == 1
    assert data["correct"] == 1
    assert data["incorrect"] == 0
    assert data["accuracy_percent"] == 100.0
