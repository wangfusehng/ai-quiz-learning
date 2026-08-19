from app.constants import MAX_MATERIAL_CHARS, MIN_MATERIAL_CHARS
from app.services.quotes import quote_in_source
from tests.fixtures import MATERIAL, QUOTE_LOSS, quiz_with_fake_quote, valid_quiz


def test_quote_matches_after_whitespace_and_quotes():
    source = "人对「确定损失」的厌恶，常常大过对同等收益的喜欢。"
    quote = "人对 确定损失 的厌恶，常常大过对同等收益的喜欢"
    assert quote_in_source(quote, source)


def test_quote_rejects_hallucination():
    assert not quote_in_source("这段话材料里根本没有", MATERIAL)


def test_create_quiz_rejects_short_material(client, quiz_gen):
    response = client.post("/v1/quizzes", json={"text": "太短了"})
    assert response.status_code == 422
    assert response.json() == {"error": "material_too_short"}
    assert quiz_gen.calls == []


def test_create_quiz_rejects_whitespace_only(client):
    response = client.post("/v1/quizzes", json={"text": "   \n\t  "})
    assert response.status_code == 422
    assert response.json()["error"] == "material_too_short"


def test_create_quiz_ok(client, quiz_gen):
    assert len(MATERIAL) >= MIN_MATERIAL_CHARS
    response = client.post("/v1/quizzes", json={"title": "损失厌恶", "text": MATERIAL})
    assert response.status_code == 200
    body = response.json()
    assert body["quizId"] == "quiz-fixture-1"
    assert body["meta"]["aiGenerated"] is True
    assert body["meta"]["thinking"] is False
    assert len(body["questions"]) == 7
    assert quiz_gen.calls[0][0] == MATERIAL
    assert quiz_gen.calls[0][1] == "损失厌恶"


def test_create_quiz_truncates_long_material(client, quiz_gen):
    text = MATERIAL + ("补充说明。" * 4000)
    assert len(text) > MAX_MATERIAL_CHARS
    response = client.post("/v1/quizzes", json={"text": text})
    assert response.status_code == 200
    sent = quiz_gen.calls[0][0]
    assert len(sent) == MAX_MATERIAL_CHARS
    assert response.json()["source"]["charCount"] == MAX_MATERIAL_CHARS


def test_create_quiz_rejects_quote_not_in_source(client, quiz_gen):
    quiz_gen.quiz = quiz_with_fake_quote()
    response = client.post("/v1/quizzes", json={"text": MATERIAL})
    assert response.status_code == 422
    assert response.json() == {"error": "quiz_invalid"}
    assert len(quiz_gen.calls) == 3


def test_create_quiz_retries_then_succeeds(client, quiz_gen):
    quiz_gen.fail_times = 2
    quiz_gen.error = RuntimeError("parse")
    response = client.post("/v1/quizzes", json={"text": MATERIAL})
    assert response.status_code == 200
    assert len(quiz_gen.calls) == 3


def test_create_quiz_model_empty(client, quiz_gen):
    from app.errors import EmptyModelError

    quiz_gen.error = EmptyModelError("empty")
    response = client.post("/v1/quizzes", json={"text": MATERIAL})
    assert response.status_code == 422
    assert response.json() == {"error": "model_empty"}


def test_create_quiz_upstream(client, quiz_gen):
    from app.errors import UpstreamError

    quiz_gen.error = UpstreamError("429")
    response = client.post("/v1/quizzes", json={"text": MATERIAL})
    assert response.status_code == 502
    assert response.json() == {"error": "upstream"}


def test_valid_fixture_quotes_exist_in_material():
    quiz = valid_quiz()
    for question in quiz.questions:
        assert quote_in_source(question.sourceQuote.text, MATERIAL)
        assert quote_in_source(QUOTE_LOSS, MATERIAL) or question.id != "q1"
