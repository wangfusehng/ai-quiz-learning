from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User
from app.schemas.user import MistakeItem, MistakeList, MistakeReviewRequest, MistakeReviewResult
from app.services.user_service import (
    delete_own_mistake,
    get_own_mistake_detail,
    list_mistakes,
    review_own_mistake,
)

router = APIRouter()


@router.get("/mistakes", response_model=MistakeList)
def read_mistakes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MistakeList:
    return MistakeList(items=list_mistakes(db, user))


@router.get("/mistakes/{mistake_id}", response_model=MistakeItem)
def read_mistake(
    mistake_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MistakeItem:
    return get_own_mistake_detail(db, user, mistake_id)


@router.post("/mistakes/{mistake_id}/review", response_model=MistakeReviewResult)
def review_mistake(
    mistake_id: int,
    body: MistakeReviewRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MistakeReviewResult:
    return review_own_mistake(db, user, mistake_id, body.optionId)


@router.delete("/mistakes/{mistake_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_mistake(
    mistake_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    delete_own_mistake(db, user, mistake_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
