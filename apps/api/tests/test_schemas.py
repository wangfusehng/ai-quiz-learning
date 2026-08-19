import pytest
from pydantic import ValidationError

from app.schemas.quiz import QuizDocument
from app.schemas.report import ReportDocument
from tests.fixtures import valid_quiz_payload, valid_report_payload


def test_quiz_schema_accepts_fixture():
    quiz = QuizDocument.model_validate(valid_quiz_payload())
    assert quiz.meta.questionCount == 7
    assert quiz.questions[-1].type == "short_answer"


def test_quiz_rejects_three_options():
    payload = valid_quiz_payload()
    payload["questions"][0]["options"] = payload["questions"][0]["options"][:3]
    with pytest.raises(ValidationError):
        QuizDocument.model_validate(payload)


def test_quiz_rejects_wrong_correct_id():
    payload = valid_quiz_payload()
    payload["questions"][0]["correctOptionId"] = "Z"
    with pytest.raises(ValidationError):
        QuizDocument.model_validate(payload)


def test_quiz_rejects_missing_short_answer():
    payload = valid_quiz_payload()
    payload["questions"] = payload["questions"][:6]
    payload["meta"]["questionCount"] = 6
    with pytest.raises(ValidationError):
        QuizDocument.model_validate(payload)


def test_quiz_rejects_empty_quote():
    payload = valid_quiz_payload()
    payload["questions"][0]["sourceQuote"]["text"] = ""
    with pytest.raises(ValidationError):
        QuizDocument.model_validate(payload)


def test_report_schema_accepts_fixture():
    report = ReportDocument.model_validate(valid_report_payload())
    assert report.aiGenerated is True
    assert len(report.pointsBitten) <= 3
