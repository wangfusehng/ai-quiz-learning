from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.quiz import QuizDocument


class QuizCreateRequest(BaseModel):
    title: str | None = None
    text: str = Field(min_length=1)


class ChoiceAnswer(BaseModel):
    questionId: str
    type: Literal["single_choice"]
    optionId: str


class ShortAnswer(BaseModel):
    questionId: str
    type: Literal["short_answer"]
    text: str


AnswerItem = ChoiceAnswer | ShortAnswer


class AnswerSheet(BaseModel):
    quizId: str
    answers: list[AnswerItem]
    startedAt: str
    submittedAt: str


class ReportCreateRequest(BaseModel):
    quiz: QuizDocument
    answers: AnswerSheet
