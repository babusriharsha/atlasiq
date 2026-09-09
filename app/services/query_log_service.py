from sqlalchemy.orm import Session

from app.models.query_log import QueryLog


def save_query_log(
    db: Session,
    question: str,
    team: str,
    model_name: str,
    latency_seconds: float,
    estimated_cost_usd: float = 0.0,
) -> QueryLog:
    query_log = QueryLog(
        question=question,
        team=team,
        model_name=model_name,
        latency_seconds=latency_seconds,
        estimated_cost_usd=estimated_cost_usd,
    )

    db.add(query_log)
    db.commit()
    db.refresh(query_log)

    return query_log
