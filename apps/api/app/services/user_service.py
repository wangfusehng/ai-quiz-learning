from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import BizError
from app.models import Mistake, QuizRecord, User
from app.schemas.quiz import Option, QuizDocument, SingleChoiceQuestion, SourceQuote
from app.schemas.report import ReportDocument
from app.schemas.requests import AnswerSheet, ChoiceAnswer
from app.schemas.user import (
    MistakeItem,
    MistakeReviewResult,
    QuizRecordDetail,
    QuizRecordItem,
    UserPublic,
)


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
    answers: AnswerSheet,
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
    db.flush()
    sync_mistakes(db, user=user, record=record, quiz=quiz, answers=answers)
    db.commit()
    db.refresh(record)
    return record


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _to_mistake_item(row: Mistake) -> MistakeItem:
    return MistakeItem(
        id=row.id,
        quizId=row.quiz_id,
        questionId=row.question_id,
        title=row.title,
        knowledgePoint=row.knowledge_point,
        stem=row.stem,
        options=[Option.model_validate(item) for item in row.options],
        correctOptionId=row.correct_option_id,
        chosenOptionId=row.chosen_option_id,
        explanation=row.explanation,
        sourceQuote=SourceQuote.model_validate(row.source_quote),
        completedAt=row.created_at,
    )


def _get_own_mistake(db: Session, user: User, mistake_id: int) -> Mistake:
    row = db.get(Mistake, mistake_id)
    if row is None or row.user_id != user.id:
        raise BizError(404, "not_found")
    return row


def sync_mistakes(
    db: Session,
    *,
    user: User,
    record: QuizRecord,
    quiz: QuizDocument,
    answers: AnswerSheet,
) -> None:
    by_id = {item.questionId: item for item in answers.answers}
    now = _utc_now()
    for question in quiz.questions:
        if not isinstance(question, SingleChoiceQuestion):
            continue
        answer = by_id.get(question.id)
        chosen = answer.optionId if isinstance(answer, ChoiceAnswer) else None
        existing = db.scalar(
            select(Mistake).where(
                Mistake.user_id == user.id,
                Mistake.quiz_id == quiz.quizId,
                Mistake.question_id == question.id,
            )
        )
        if chosen is None or chosen == question.correctOptionId:
            if existing is not None:
                db.delete(existing)
            continue
        payload = {
            "record_id": record.id,
            "title": quiz.source.title,
            "knowledge_point": question.knowledgePoint,
            "stem": question.stem,
            "options": [item.model_dump(mode="json") for item in question.options],
            "correct_option_id": question.correctOptionId,
            "chosen_option_id": chosen,
            "explanation": question.explanation,
            "source_quote": question.sourceQuote.model_dump(mode="json"),
            "created_at": now,
        }
        if existing is None:
            db.add(
                Mistake(
                    user_id=user.id,
                    quiz_id=quiz.quizId,
                    question_id=question.id,
                    **payload,
                )
            )
            continue
        for key, value in payload.items():
            setattr(existing, key, value)


def list_mistakes(db: Session, user: User) -> list[MistakeItem]:
    rows = db.scalars(
        select(Mistake)
        .where(Mistake.user_id == user.id)
        .order_by(Mistake.created_at.desc(), Mistake.id.desc())
        .limit(200)
    ).all()
    return [_to_mistake_item(row) for row in rows]


def get_own_mistake_detail(db: Session, user: User, mistake_id: int) -> MistakeItem:
    return _to_mistake_item(_get_own_mistake(db, user, mistake_id))


def review_own_mistake(
    db: Session,
    user: User,
    mistake_id: int,
    option_id: str,
) -> MistakeReviewResult:
    row = _get_own_mistake(db, user, mistake_id)
    option_ids = {item.get("id") for item in row.options if isinstance(item, dict)}
    if option_id not in option_ids:
        raise BizError(422, "quiz_invalid")
    if option_id == row.correct_option_id:
        db.delete(row)
        db.commit()
        return MistakeReviewResult(mastered=True, item=None)
    row.chosen_option_id = option_id
    row.created_at = _utc_now()
    db.add(row)
    db.commit()
    db.refresh(row)
    return MistakeReviewResult(mastered=False, item=_to_mistake_item(row))


def delete_own_mistake(db: Session, user: User, mistake_id: int) -> None:
    row = _get_own_mistake(db, user, mistake_id)
    db.delete(row)
    db.commit()


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
