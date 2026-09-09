from sqlalchemy.orm import Session

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
