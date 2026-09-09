from app.models.query_log import QueryLog
from tests.conftest import TestingSessionLocal, client


def test_query_metrics():
    db = TestingSessionLocal()

    try:
        db.add_all([
            QueryLog(
                question="Question 1",
                team="engineering",
                model_name="llama3.2:3b",
                latency_seconds=2.0,
                estimated_cost_usd=0.0,
            ),
            QueryLog(
                question="Question 2",
                team="engineering",
                model_name="llama3.2:3b",
                latency_seconds=4.0,
                estimated_cost_usd=0.0,
            ),
        ])

        db.commit()

    finally:
        db.close()

    response = client.get("/metrics/queries")

    assert response.status_code == 200

    data = response.json()

    assert data["total_queries"] == 2
    assert data["average_latency_seconds"] == 3.0
    assert data["average_cost_usd"] == 0.0
    assert data["total_cost_usd"] == 0.0


def test_query_metrics_by_team():
    db = TestingSessionLocal()

    try:
        db.add_all([
            QueryLog(
                question="Engineering question",
                team="engineering",
                model_name="llama3.2:3b",
                latency_seconds=2.0,
                estimated_cost_usd=0.0,
            ),
            QueryLog(
                question="Support question",
                team="customer_support",
                model_name="llama3.2:3b",
                latency_seconds=8.0,
                estimated_cost_usd=0.0,
            ),
        ])

        db.commit()

    finally:
        db.close()

    response = client.get(
        "/metrics/queries?team=engineering"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_queries"] == 1
    assert data["average_latency_seconds"] == 2.0
