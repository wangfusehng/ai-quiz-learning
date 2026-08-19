from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db, get_wechat_client
from app.errors import BizError, UpstreamError
from app.schemas.user import AuthResponse, WeChatLoginRequest
from app.security import issue_access_token
from app.services.user_service import get_or_create_by_openid, to_public
from app.services.wechat import WeChatAuthClient

router = APIRouter()


@router.post("/auth/wechat", response_model=AuthResponse)
def wechat_login(
    body: WeChatLoginRequest,
    db: Session = Depends(get_db),
    wechat: WeChatAuthClient = Depends(get_wechat_client),
) -> AuthResponse:
    try:
        openid = wechat.exchange_code(body.code.strip())
    except UpstreamError as exc:
        raise BizError(502, "upstream") from exc
    if not openid:
        raise BizError(502, "upstream")
    user = get_or_create_by_openid(db, openid)
    return AuthResponse(token=issue_access_token(user.id), user=to_public(user))
