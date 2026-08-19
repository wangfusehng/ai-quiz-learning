from app.errors import EmptyModelError, UpstreamError
from app.main import create_app
from app.deps import get_quiz_generator, get_report_generator, get_wechat_client
from app.db import Base
from app.schemas.quiz import QuizDocument
from app.schemas.report import ReportDocument
from tests.fixtures import valid_quiz, valid_report_payload

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
import pytest


class FakeQuizGenerator:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str | None]] = []
        self.quiz: QuizDocument | None = valid_quiz()
        self.error: Exception | None = None
        self.fail_times = 0
        self._n = 0

    def generate(self, *, text: str, title: str | None) -> QuizDocument:
        self.calls.append((text, title))
        self._n += 1
        if self._n <= self.fail_times and self.error is not None:
            raise self.error
        if self.error is not None and self.fail_times == 0:
            raise self.error
        assert self.quiz is not None
        return self.quiz


class FakeReportGenerator:
    def __init__(self) -> None:
        self.calls = []
        self.report = ReportDocument.model_validate(valid_report_payload())
        self.error: Exception | None = None

    def generate(self, *, quiz, answers) -> ReportDocument:
        self.calls.append((quiz, answers))
        if self.error is not None:
            raise self.error
        return self.report


class FakeWeChat:
    def __init__(self) -> None:
        self.openid_by_code: dict[str, str] = {}
        self.default_openid = "oTESTOPENID"
        self.fail = False

    def exchange_code(self, code: str) -> str:
        if self.fail:
            raise UpstreamError("wechat")
        return self.openid_by_code.get(code, self.default_openid)


@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def quiz_gen() -> FakeQuizGenerator:
    return FakeQuizGenerator()


@pytest.fixture
def report_gen() -> FakeReportGenerator:
    return FakeReportGenerator()


@pytest.fixture
def wechat() -> FakeWeChat:
    return FakeWeChat()


@pytest.fixture
def client(
    quiz_gen: FakeQuizGenerator,
    report_gen: FakeReportGenerator,
    wechat: FakeWeChat,
    db_engine,
) -> TestClient:
    app = create_app(engine=db_engine)
    app.dependency_overrides[get_quiz_generator] = lambda: quiz_gen
    app.dependency_overrides[get_report_generator] = lambda: report_gen
    app.dependency_overrides[get_wechat_client] = lambda: wechat
    return TestClient(app)


def auth_header(client: TestClient, *, code: str = "wx-code") -> dict[str, str]:
    response = client.post("/v1/auth/wechat", json={"code": code})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['token']}"}
