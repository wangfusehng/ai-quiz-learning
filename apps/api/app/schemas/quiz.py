from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.constants import (
    CHOICE_OPTION_COUNT,
    DEFAULT_MODEL,
    EXCERPT_CHARS,
    MAX_QUESTIONS,
    MIN_QUESTIONS,
    QUOTE_MAX_CHARS,
)


class SourceQuote(BaseModel):
    text: str = Field(min_length=1, max_length=QUOTE_MAX_CHARS)
    locator: str = Field(min_length=1)


class Option(BaseModel):
    id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class Rubric(BaseModel):
    keyPoints: list[str] = Field(min_length=1)


class SourceInfo(BaseModel):
    type: Literal["text"] = "text"
    title: str = Field(min_length=1)
    excerpt: str = ""
    charCount: int = Field(ge=0)


class QuizMeta(BaseModel):
    model: str = DEFAULT_MODEL
    thinking: bool = False
    questionCount: int = Field(ge=MIN_QUESTIONS, le=MAX_QUESTIONS)
    estimatedMinutes: int = Field(ge=1, le=15, default=8)
    aiGenerated: bool = True


class SingleChoiceQuestion(BaseModel):
    id: str
    type: Literal["single_choice"]
    stem: str = Field(min_length=1)
    options: list[Option]
    correctOptionId: str
    explanation: str = Field(min_length=1)
    sourceQuote: SourceQuote
    knowledgePoint: str = Field(min_length=1)

    @field_validator("options")
    @classmethod
    def four_options(cls, value: list[Option]) -> list[Option]:
        if len(value) != CHOICE_OPTION_COUNT:
            raise ValueError("single_choice must have exactly 4 options")
        ids = [item.id for item in value]
        if len(set(ids)) != len(ids):
            raise ValueError("option ids must be unique")
        return value

    @model_validator(mode="after")
    def correct_option_exists(self) -> "SingleChoiceQuestion":
        ids = {item.id for item in self.options}
        if self.correctOptionId not in ids:
            raise ValueError("correctOptionId must be one of the options")
        return self


class ShortAnswerQuestion(BaseModel):
    id: str
    type: Literal["short_answer"]
    stem: str = Field(min_length=1)
    rubric: Rubric
    explanation: str = Field(min_length=1)
    sourceQuote: SourceQuote
    knowledgePoint: str = Field(min_length=1)


Question = Annotated[
    SingleChoiceQuestion | ShortAnswerQuestion,
    Field(discriminator="type"),
]


class QuizDocument(BaseModel):
    schemaVersion: Literal["1"] = "1"
    quizId: str = Field(min_length=1)
    source: SourceInfo
    meta: QuizMeta
    questions: list[Question]

    @field_validator("questions")
    @classmethod
    def question_mix(cls, value: list[Question]) -> list[Question]:
        if not MIN_QUESTIONS <= len(value) <= MAX_QUESTIONS:
            raise ValueError("questions must contain 6 to 10 items")
        ids = [item.id for item in value]
        if len(set(ids)) != len(ids):
            raise ValueError("question ids must be unique")
        if not any(item.type == "single_choice" for item in value):
            raise ValueError("quiz must include single_choice questions")
        if not any(item.type == "short_answer" for item in value):
            raise ValueError("quiz must include one short_answer question")
        return value


def excerpt_of(text: str) -> str:
    compact = "".join(text.split())
    return compact[:EXCERPT_CHARS]
