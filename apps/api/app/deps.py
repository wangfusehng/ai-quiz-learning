from functools import lru_cache

from app.services.quiz_service import QuizGenerator
from app.services.report_service import ReportGenerator


@lru_cache
def get_quiz_generator() -> QuizGenerator:
    from app.chains.quiz import LangChainQuizGenerator

    return LangChainQuizGenerator()


@lru_cache
def get_report_generator() -> ReportGenerator:
    from app.chains.report import LangChainReportGenerator

    return LangChainReportGenerator()
