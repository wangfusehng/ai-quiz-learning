from fastapi import APIRouter, Depends

from app.deps import get_report_generator
from app.schemas.report import ReportDocument
from app.schemas.requests import ReportCreateRequest
from app.services.report_service import ReportGenerator, create_report

router = APIRouter()


@router.post("/reports", response_model=ReportDocument)
def create_report_endpoint(
    body: ReportCreateRequest,
    generator: ReportGenerator = Depends(get_report_generator),
) -> ReportDocument:
    return create_report(quiz=body.quiz, answers=body.answers, generator=generator)
