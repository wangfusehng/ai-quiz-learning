from app.errors import BizError, EmptyModelError, UpstreamError
from app.schemas.quiz import QuizDocument, SingleChoiceQuestion
from app.schemas.report import ReportDocument, ScoreHint
from app.schemas.requests import AnswerSheet, ChoiceAnswer


class ReportGenerator:
    def generate(self, *, quiz: QuizDocument, answers: AnswerSheet) -> ReportDocument:
        raise NotImplementedError


def choice_score(quiz: QuizDocument, answers: AnswerSheet) -> ScoreHint:
    by_id = {item.questionId: item for item in answers.answers}
    correct = 0
    total = 0
    for question in quiz.questions:
        if not isinstance(question, SingleChoiceQuestion):
            continue
        total += 1
        answer = by_id.get(question.id)
        if isinstance(answer, ChoiceAnswer) and answer.optionId == question.correctOptionId:
            correct += 1
    return ScoreHint(
        correct=correct,
        total=total,
        shortAnswerNote="短答不计入对错题数，不打百分制羞辱。",
    )


def slim_quiz_for_model(quiz: QuizDocument, answers: AnswerSheet) -> dict:
    by_id = {item.questionId: item for item in answers.answers}
    questions = []
    for question in quiz.questions:
        row = {
            "id": question.id,
            "type": question.type,
            "knowledgePoint": question.knowledgePoint,
            "sourceQuote": question.sourceQuote.model_dump(),
            "stem": question.stem,
        }
        if isinstance(question, SingleChoiceQuestion):
            answer = by_id.get(question.id)
            chosen = answer.optionId if isinstance(answer, ChoiceAnswer) else None
            row["correctOptionId"] = question.correctOptionId
            row["chosenOptionId"] = chosen
            row["isCorrect"] = chosen == question.correctOptionId
        else:
            answer = by_id.get(question.id)
            row["rubric"] = question.rubric.model_dump()
            row["userText"] = getattr(answer, "text", "")
        questions.append(row)
    return {
        "quizId": quiz.quizId,
        "title": quiz.source.title,
        "questions": questions,
    }


def create_report(
    *,
    quiz: QuizDocument,
    answers: AnswerSheet,
    generator: ReportGenerator,
) -> ReportDocument:
    if answers.quizId != quiz.quizId:
        raise BizError(422, "quiz_invalid")
    last_error = "quiz_invalid"
    for _ in range(3):
        try:
            report = generator.generate(quiz=quiz, answers=answers)
            parsed = ReportDocument.model_validate(report)
        except EmptyModelError:
            last_error = "model_empty"
            continue
        except UpstreamError as exc:
            raise BizError(502, "upstream") from exc
        except Exception:
            last_error = "quiz_invalid"
            continue
        payload = parsed.model_dump()
        payload["quizId"] = quiz.quizId
        payload["aiGenerated"] = True
        payload["scoreHint"] = choice_score(quiz, answers).model_dump()
        gold = payload["goldQuote"]["text"]
        allowed = {item.sourceQuote.text for item in quiz.questions}
        if gold not in allowed:
            # keep locator but force a known quote if the model drifted
            first = quiz.questions[0].sourceQuote
            payload["goldQuote"] = first.model_dump()
        return ReportDocument.model_validate(payload)
    raise BizError(422, last_error)
