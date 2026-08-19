from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db, get_optional_user, get_report_generator
from app.models import User
from app.schemas.report import ReportDocument
from app.schemas.requests import ReportCreateRequest
from app.services.report_service import ReportGenerator, create_report
from app.services.user_service import save_quiz_record

router = APIRouter()


@router.post("/reports", response_model=ReportDocument)
def create_report_endpoint(
    body: ReportCreateRequest,
    generator: ReportGenerator = Depends(get_report_generator),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
) -> ReportDocument:
    report = create_report(quiz=body.quiz, answers=body.answers, generator=generator)
    if user is not None:
        try:
            save_quiz_record(db, user=user, quiz=body.quiz, report=report, answers=body.answers)
        except Exception:
            db.rollback()
    return report
