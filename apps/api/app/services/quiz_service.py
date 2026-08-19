from uuid import uuid4

from app.constants import LLM_ATTEMPTS, MAX_MATERIAL_CHARS, MIN_MATERIAL_CHARS
from app.errors import BizError, EmptyModelError, UpstreamError
from app.schemas.quiz import QuizDocument, excerpt_of
from app.services.quotes import missing_quote_ids


class QuizGenerator:
    def generate(self, *, text: str, title: str | None) -> QuizDocument:
        raise NotImplementedError


def prepare_material(text: str) -> str:
    normalized = text.strip()
    if len(normalized) < MIN_MATERIAL_CHARS:
        raise BizError(422, "material_too_short")
    if len(normalized) > MAX_MATERIAL_CHARS:
        return normalized[:MAX_MATERIAL_CHARS]
    return normalized


def finalize_quiz(quiz: QuizDocument, *, text: str, title: str | None, model_name: str) -> QuizDocument:
    payload = quiz.model_dump()
    payload["source"]["type"] = "text"
    payload["source"]["charCount"] = len(text)
    payload["source"]["excerpt"] = excerpt_of(text)
    if title and title.strip():
        payload["source"]["title"] = title.strip()
    payload["meta"]["model"] = model_name
    payload["meta"]["thinking"] = False
    payload["meta"]["aiGenerated"] = True
    payload["meta"]["questionCount"] = len(quiz.questions)
    if not payload.get("quizId"):
        payload["quizId"] = str(uuid4())
    return QuizDocument.model_validate(payload)


def create_quiz(
    *,
    text: str,
    title: str | None,
    generator: QuizGenerator,
    model_name: str,
) -> QuizDocument:
    material = prepare_material(text)
    last_error = "quiz_invalid"
    for _ in range(LLM_ATTEMPTS):
        try:
            raw = generator.generate(text=material, title=title)
            quiz = QuizDocument.model_validate(raw)
        except EmptyModelError:
            last_error = "model_empty"
            continue
        except UpstreamError as exc:
            raise BizError(502, "upstream") from exc
        except Exception:
            last_error = "quiz_invalid"
            continue
        if missing_quote_ids(quiz.questions, material):
            last_error = "quiz_invalid"
            continue
        return finalize_quiz(quiz, text=material, title=title, model_name=model_name)
    raise BizError(422, last_error)
