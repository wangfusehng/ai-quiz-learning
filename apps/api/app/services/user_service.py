from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import BizError
from app.models import QuizRecord, User
from app.schemas.quiz import QuizDocument
from app.schemas.report import ReportDocument
from app.schemas.user import QuizRecordDetail, QuizRecordItem, UserPublic


def to_public(user: User) -> UserPublic:
    return UserPublic(
        id=user.id,
        nickname=user.nickname,
        avatarUrl=user.avatar_url,
        wechatConnected=True,
    )


def get_or_create_by_openid(db: Session, openid: str) -> User:
    user = db.scalar(select(User).where(User.openid == openid))
    if user is not None:
        return user
    user = User(openid=openid)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_profile(db: Session, user: User, *, nickname: str | None, avatar_url: str | None) -> User:
    if nickname is not None:
        stripped = nickname.strip()
        user.nickname = stripped or None
    if avatar_url is not None:
        stripped_url = avatar_url.strip()
        user.avatar_url = stripped_url or None
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def save_quiz_record(
    db: Session,
    *,
    user: User,
    quiz: QuizDocument,
    report: ReportDocument,
) -> QuizRecord:
    record = QuizRecord(
        user_id=user.id,
        quiz_id=quiz.quizId,
        title=quiz.source.title,
        correct=report.scoreHint.correct,
        total=report.scoreHint.total,
        completed_at=datetime.now(timezone.utc).replace(tzinfo=None),
        quiz_json=quiz.model_dump(mode="json"),
        report_json=report.model_dump(mode="json"),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_records(db: Session, user: User) -> list[QuizRecordItem]:
    rows = db.scalars(
        select(QuizRecord)
        .where(QuizRecord.user_id == user.id)
        .order_by(QuizRecord.completed_at.desc(), QuizRecord.id.desc())
        .limit(100)
    ).all()
    return [
        QuizRecordItem(
            id=row.id,
            quizId=row.quiz_id,
            title=row.title,
            correct=row.correct,
            total=row.total,
            completedAt=row.completed_at,
            quiz=QuizDocument.model_validate(row.quiz_json) if row.quiz_json else None,
        )
        for row in rows
    ]


def get_own_record_detail(db: Session, user: User, record_id: int) -> QuizRecordDetail:
    row = db.get(QuizRecord, record_id)
    if row is None or row.user_id != user.id:
        raise BizError(404, "not_found")
    if not row.quiz_json:
        raise BizError(422, "quiz_invalid")
    return QuizRecordDetail(
        id=row.id,
        quizId=row.quiz_id,
        title=row.title,
        correct=row.correct,
        total=row.total,
        completedAt=row.completed_at,
        quiz=QuizDocument.model_validate(row.quiz_json),
    )
