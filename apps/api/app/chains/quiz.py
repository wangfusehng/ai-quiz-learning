from uuid import uuid4

from app.chains.llm import build_chat_model
from app.chains.prompts import QUIZ_SYSTEM_PROMPT
from app.config import get_settings
from app.errors import EmptyModelError, UpstreamError
from app.schemas.quiz import QuizDocument
from app.services.quiz_service import QuizGenerator


class LangChainQuizGenerator(QuizGenerator):
    def generate(self, *, text: str, title: str | None) -> QuizDocument:
        try:
            model = build_chat_model()
            structured = model.with_structured_output(QuizDocument, method="json_mode")
            heading = title.strip() if title and title.strip() else "（未填标题）"
            human = (
                f"title: {heading}\n"
                "请出 6 道单选 + 1 道短答。sourceQuote.text 必须从下面材料中复制。\n\n"
                f"{text}"
            )
            result = structured.invoke(
                [
                    ("system", QUIZ_SYSTEM_PROMPT),
                    ("human", human),
                ]
            )
        except Exception as exc:
            name = type(exc).__name__.lower()
            message = str(exc).lower()
            if "empty" in message or "content" in message and "none" in message:
                raise EmptyModelError(str(exc)) from exc
            if any(token in name or token in message for token in ("timeout", "429", "rate", "connect", "api")):
                raise UpstreamError(str(exc)) from exc
            raise EmptyModelError(str(exc)) from exc
        if result is None:
            raise EmptyModelError("empty structured output")
        quiz = QuizDocument.model_validate(result)
        if not quiz.quizId:
            quiz = quiz.model_copy(update={"quizId": str(uuid4())})
        quiz = quiz.model_copy(
            update={
                "meta": quiz.meta.model_copy(
                    update={"model": get_settings().deepseek_model or "deepseek-v4-flash", "thinking": False}
                )
            }
        )
        return quiz
