from fastapi import APIRouter, Depends

from app.config import get_settings
from app.deps import get_quiz_generator
from app.schemas.quiz import QuizDocument
from app.schemas.requests import QuizCreateRequest
from app.services.quiz_service import QuizGenerator, create_quiz

router = APIRouter()


@router.post("/quizzes", response_model=QuizDocument)
def create_quiz_endpoint(
    body: QuizCreateRequest,
    generator: QuizGenerator = Depends(get_quiz_generator),
) -> QuizDocument:
    settings = get_settings()
    return create_quiz(
        text=body.text,
        title=body.title,
        generator=generator,
        model_name=settings.deepseek_model or "deepseek-v4-flash",
    )
