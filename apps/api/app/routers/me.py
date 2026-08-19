from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User
from app.schemas.user import UserPublic, UserUpdateRequest
from app.services.user_service import to_public, update_profile

router = APIRouter()


@router.get("/me", response_model=UserPublic)
def read_me(user: User = Depends(get_current_user)) -> UserPublic:
    return to_public(user)


@router.put("/me", response_model=UserPublic)
def update_me(
    body: UserUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> UserPublic:
    updated = update_profile(
        db,
        user,
        nickname=body.nickname,
        avatar_url=body.avatarUrl,
    )
    return to_public(updated)
