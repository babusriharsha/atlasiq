from typing import Literal

from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    question: str
    answer: str
    team: str
    rating: Literal["correct", "incorrect"]
    correction: str | None = None
