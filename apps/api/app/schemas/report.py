from typing import Literal

from pydantic import BaseModel, Field


class GoldQuote(BaseModel):
    text: str = Field(min_length=1)
    locator: str = Field(min_length=1)


class ScoreHint(BaseModel):
    correct: int = Field(ge=0)
    total: int = Field(ge=0)
    shortAnswerNote: str = ""


class ReportDocument(BaseModel):
    schemaVersion: Literal["1"] = "1"
    quizId: str = Field(min_length=1)
    aiGenerated: bool = True
    headline: str = Field(min_length=1)
    oneLiner: str = Field(min_length=1)
    pointsBitten: list[str] = Field(max_length=3)
    stillFuzzy: list[str] = Field(max_length=3)
    goldQuote: GoldQuote
    invite: str = Field(min_length=1)
    scoreHint: ScoreHint
