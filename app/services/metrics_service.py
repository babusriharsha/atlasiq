from sqlalchemy.orm import Session
from app.models.query_log import QueryLog
from app.models.feedback import Feedback


def get_feedback_metrics(
    db: Session,
    team: str | None = None,
) -> dict:
    query = db.query(Feedback)

    if team:
        query = query.filter(Feedback.team == team)

    feedback = query.all()

    total = len(feedback)
    correct = sum(
        1 for item in feedback
        if item.rating == "correct"
    )
    incorrect = sum(
        1 for item in feedback
        if item.rating == "incorrect"
    )

    accuracy = (
        round((correct / total) * 100, 2)
        if total > 0
        else 0.0
    )

    return {
        "total_feedback": total,
        "correct": correct,
        "incorrect": incorrect,
        "accuracy_percent": accuracy,
    }
def get_query_metrics(
    db: Session,
    team: str | None = None,
) -> dict:
    query = db.query(QueryLog)

    if team:
        query = query.filter(QueryLog.team == team)

    logs = query.all()

    total_queries = len(logs)

    if total_queries == 0:
        return {
            "total_queries": 0,
            "average_latency_seconds": 0.0,
            "average_cost_usd": 0.0,
            "total_cost_usd": 0.0,
        }

    total_latency = sum(
        log.latency_seconds for log in logs
    )

    total_cost = sum(
        log.estimated_cost_usd for log in logs
    )

    return {
        "total_queries": total_queries,
        "average_latency_seconds": round(
            total_latency / total_queries,
            3,
        ),
        "average_cost_usd": round(
            total_cost / total_queries,
            6,
        ),
        "total_cost_usd": round(total_cost, 6),
    }
