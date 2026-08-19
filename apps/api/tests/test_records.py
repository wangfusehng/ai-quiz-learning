from tests.conftest import auth_header
from tests.fixtures import sample_answers, valid_quiz_payload


def test_records_requires_token(client):
    response = client.get("/v1/records")
    assert response.status_code == 401
    assert response.json() == {"error": "unauthorized"}


def test_records_empty_after_login(client):
    headers = auth_header(client)
    response = client.get("/v1/records", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_report_without_token_does_not_create_record(client):
    headers = auth_header(client)
    response = client.post(
        "/v1/reports",
        json={"quiz": valid_quiz_payload(), "answers": sample_answers(wrong_first=True)},
    )
    assert response.status_code == 200
    listed = client.get("/v1/records", headers=headers)
    assert listed.json() == {"items": []}


def test_report_with_token_creates_own_record(client):
    headers = auth_header(client, code="user-a")
    response = client.post(
        "/v1/reports",
        headers=headers,
        json={"quiz": valid_quiz_payload(), "answers": sample_answers(wrong_first=True)},
    )
    assert response.status_code == 200
    listed = client.get("/v1/records", headers=headers)
    assert listed.status_code == 200
    items = listed.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "损失厌恶"
    assert items[0]["correct"] == 4
    assert items[0]["total"] == 6
    assert items[0]["quizId"] == "quiz-fixture-1"
    assert items[0]["completedAt"]
    assert items[0]["quiz"]["quizId"] == "quiz-fixture-1"
    assert items[0]["quiz"]["questions"]


def test_records_are_isolated_per_user(client, wechat):
    wechat.openid_by_code["a"] = "openid-a"
    wechat.openid_by_code["b"] = "openid-b"
    headers_a = auth_header(client, code="a")
    headers_b = auth_header(client, code="b")
    created = client.post(
        "/v1/reports",
        headers=headers_a,
        json={"quiz": valid_quiz_payload(), "answers": sample_answers()},
    )
    assert created.status_code == 200
    a_items = client.get("/v1/records", headers=headers_a).json()["items"]
    b_items = client.get("/v1/records", headers=headers_b).json()["items"]
    assert len(a_items) == 1
    assert b_items == []


def test_get_record_returns_quiz_for_replay(client):
    headers = auth_header(client)
    created = client.post(
        "/v1/reports",
        headers=headers,
        json={"quiz": valid_quiz_payload(), "answers": sample_answers()},
    )
    assert created.status_code == 200
    record_id = client.get("/v1/records", headers=headers).json()["items"][0]["id"]
    detail = client.get(f"/v1/records/{record_id}", headers=headers)
    assert detail.status_code == 200
    body = detail.json()
    assert body["quiz"]["quizId"] == "quiz-fixture-1"
    assert body["quiz"]["questions"]


def test_get_record_hidden_from_other_user(client, wechat):
    wechat.openid_by_code["a"] = "openid-a"
    wechat.openid_by_code["b"] = "openid-b"
    headers_a = auth_header(client, code="a")
    headers_b = auth_header(client, code="b")
    client.post(
        "/v1/reports",
        headers=headers_a,
        json={"quiz": valid_quiz_payload(), "answers": sample_answers()},
    )
    record_id = client.get("/v1/records", headers=headers_a).json()["items"][0]["id"]
    hidden = client.get(f"/v1/records/{record_id}", headers=headers_b)
    assert hidden.status_code == 404
    assert hidden.json() == {"error": "not_found"}
