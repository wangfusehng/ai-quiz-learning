from functools import lru_cache

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.errors import BizError
from app.models import User
from app.security import parse_access_token
from app.services.quiz_service import QuizGenerator
from app.services.report_service import ReportGenerator
from app.services.wechat import WeChatAuthClient

_bearer = HTTPBearer(auto_error=False)


@lru_cache
def get_quiz_generator() -> QuizGenerator:
    from app.chains.quiz import LangChainQuizGenerator

    return LangChainQuizGenerator()


@lru_cache
def get_report_generator() -> ReportGenerator:
    from app.chains.report import LangChainReportGenerator

    return LangChainReportGenerator()


@lru_cache
def get_wechat_client() -> WeChatAuthClient:
    from app.services.wechat import HttpWeChatAuthClient

    return HttpWeChatAuthClient()


def get_db(request: Request):
    db = request.app.state.session_factory()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if creds is None or creds.scheme.lower() != "bearer" or not creds.credentials:
        raise BizError(401, "unauthorized")
    user_id = parse_access_token(creds.credentials)
    user = db.get(User, user_id)
    if user is None:
        raise BizError(401, "unauthorized")
    return user


def get_optional_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User | None:
    if creds is None or creds.scheme.lower() != "bearer" or not creds.credentials:
        return None
    try:
        user_id = parse_access_token(creds.credentials)
    except BizError:
        return None
    return db.get(User, user_id)
