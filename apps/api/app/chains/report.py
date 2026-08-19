import json

from app.chains.llm import build_chat_model
from app.chains.prompts import REPORT_SYSTEM_PROMPT
from app.errors import EmptyModelError, UpstreamError
from app.schemas.quiz import QuizDocument
from app.schemas.report import ReportDocument
from app.schemas.requests import AnswerSheet
from app.services.report_service import ReportGenerator, slim_quiz_for_model


class LangChainReportGenerator(ReportGenerator):
    def generate(self, *, quiz: QuizDocument, answers: AnswerSheet) -> ReportDocument:
        try:
            model = build_chat_model()
            structured = model.with_structured_output(ReportDocument, method="json_mode")
            payload = slim_quiz_for_model(quiz, answers)
            human = "请根据下面的关卡摘要和作答生成报告 json。\n" + json.dumps(
                payload, ensure_ascii=False
            )
            result = structured.invoke(
                [
                    ("system", REPORT_SYSTEM_PROMPT),
                    ("human", human),
                ]
            )
        except Exception as exc:
            message = str(exc).lower()
            if any(token in message for token in ("timeout", "429", "rate", "connect")):
                raise UpstreamError(str(exc)) from exc
            raise EmptyModelError(str(exc)) from exc
        if result is None:
            raise EmptyModelError("empty structured output")
        return ReportDocument.model_validate(result)
