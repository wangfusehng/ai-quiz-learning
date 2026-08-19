from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.quiz import QuizDocument


class WeChatLoginRequest(BaseModel):
    code: str = Field(min_length=1)


class UserPublic(BaseModel):
    id: int
    nickname: str | None = None
    avatarUrl: str | None = None
    wechatConnected: bool = True


class AuthResponse(BaseModel):
    token: str
    user: UserPublic


class UserUpdateRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=64)
    avatarUrl: str | None = Field(default=None, max_length=512)


class QuizRecordItem(BaseModel):
    id: int
    quizId: str
    title: str
    correct: int
    total: int
    completedAt: datetime
    quiz: QuizDocument | None = None


class QuizRecordList(BaseModel):
    items: list[QuizRecordItem]


class QuizRecordDetail(QuizRecordItem):
    quiz: QuizDocument
