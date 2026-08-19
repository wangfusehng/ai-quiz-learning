from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User
from app.schemas.user import QuizRecordDetail, QuizRecordList
from app.services.user_service import get_own_record_detail, list_records

router = APIRouter()


@router.get("/records", response_model=QuizRecordList)
def read_records(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> QuizRecordList:
    return QuizRecordList(items=list_records(db, user))


@router.get("/records/{record_id}", response_model=QuizRecordDetail)
def read_record(
    record_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> QuizRecordDetail:
    return get_own_record_detail(db, user, record_id)
