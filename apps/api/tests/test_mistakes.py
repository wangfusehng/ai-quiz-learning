from copy import deepcopy

from tests.conftest import auth_header
from tests.fixtures import sample_answers, valid_quiz_payload


def _all_correct_answers() -> dict:
    payload = deepcopy(sample_answers())
    for item in payload["answers"]:
        if item["type"] == "single_choice":
            item["optionId"] = "B"
    return payload


def _by_question(items: list[dict]) -> dict[str, dict]:
    return {item["questionId"]: item for item in items}


def test_mistakes_requires_token(client):
    response = client.get("/v1/mistakes")
    assert response.status_code == 401
    assert response.json() == {"error": "unauthorized"}


def test_mistakes_empty_after_login(client):
    headers = auth_header(client)
    response = client.get("/v1/mistakes", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_report_collects_wrong_choices_not_short_answer(client):
    headers = auth_header(client)
    created = client.post(
        "/v1/reports",
        headers=headers,
        json={"quiz": valid_quiz_payload(), "answers": sample_answers(wrong_first=True)},
    )
    assert created.status_code == 200
    listed = client.get("/v1/mistakes", headers=headers)
    assert listed.status_code == 200
    items = listed.json()["items"]
    by_id = _by_question(items)
    assert set(by_id) == {"q1", "q6"}
    assert by_id["q1"]["stem"] == "哪句更贴近材料？"
    assert by_id["q1"]["title"] == "损失厌恶"
    assert by_id["q1"]["knowledgePoint"] == "损失厌恶"
    assert by_id["q1"]["chosenOptionId"] == "A"
    assert by_id["q1"]["correctOptionId"] == "B"
    assert by_id["q1"]["explanation"]
    assert by_id["q1"]["sourceQuote"]["text"]
    assert by_id["q1"]["options"]
    assert by_id["q6"]["chosenOptionId"] == "A"
    assert all(item["questionId"] != "q7" for item in items)


def test_mistakes_are_isolated_per_user(client, wechat):
    wechat.openid_by_code["a"] = "openid-a"
    wechat.openid_by_code["b"] = "openid-b"
    headers_a = auth_header(client, code="a")
    headers_b = auth_header(client, code="b")
    created = client.post(
        "/v1/reports",
        headers=headers_a,
        json={"quiz": valid_quiz_payload(), "answers": sample_answers(wrong_first=True)},
    )
    assert created.status_code == 200
    a_items = client.get("/v1/mistakes", headers=headers_a).json()["items"]
    b_items = client.get("/v1/mistakes", headers=headers_b).json()["items"]
    assert len(a_items) == 2
    assert b_items == []


def test_all_correct_replay_removes_mistakes(client):
    headers = auth_header(client)
    first = client.post(
        "/v1/reports",
        headers=headers,
        json={"quiz": valid_quiz_payload(), "answers": sample_answers(wrong_first=True)},
    )
    assert first.status_code == 200
    assert len(client.get("/v1/mistakes", headers=headers).json()["items"]) == 2
    second = client.post(
        "/v1/reports",
        headers=headers,
        json={"quiz": valid_quiz_payload(), "answers": _all_correct_answers()},
    )
    assert second.status_code == 200
    assert client.get("/v1/mistakes", headers=headers).json() == {"items": []}


def test_review_correct_removes_mistake(client):
    headers = auth_header(client)
    client.post(
        "/v1/reports",
        headers=headers,
        json={"quiz": valid_quiz_payload(), "answers": sample_answers(wrong_first=True)},
    )
    items = client.get("/v1/mistakes", headers=headers).json()["items"]
    q1 = _by_question(items)["q1"]
    reviewed = client.post(
        f"/v1/mistakes/{q1['id']}/review",
        headers=headers,
        json={"optionId": "B"},
    )
    assert reviewed.status_code == 200
    assert reviewed.json() == {"mastered": True, "item": None}
    remaining = client.get("/v1/mistakes", headers=headers).json()["items"]
    assert set(_by_question(remaining)) == {"q6"}


def test_review_wrong_keeps_and_updates_choice(client):
    headers = auth_header(client)
    client.post(
        "/v1/reports",
        headers=headers,
        json={"quiz": valid_quiz_payload(), "answers": sample_answers(wrong_first=True)},
    )
    q1 = _by_question(client.get("/v1/mistakes", headers=headers).json()["items"])["q1"]
    reviewed = client.post(
        f"/v1/mistakes/{q1['id']}/review",
        headers=headers,
        json={"optionId": "C"},
    )
    assert reviewed.status_code == 200
    body = reviewed.json()
    assert body["mastered"] is False
    assert body["item"]["id"] == q1["id"]
    assert body["item"]["chosenOptionId"] == "C"
    remaining = client.get("/v1/mistakes", headers=headers).json()["items"]
    assert _by_question(remaining)["q1"]["chosenOptionId"] == "C"


def test_delete_mistake(client):
    headers = auth_header(client)
    client.post(
        "/v1/reports",
        headers=headers,
        json={"quiz": valid_quiz_payload(), "answers": sample_answers(wrong_first=True)},
    )
    q1 = _by_question(client.get("/v1/mistakes", headers=headers).json()["items"])["q1"]
    removed = client.delete(f"/v1/mistakes/{q1['id']}", headers=headers)
    assert removed.status_code == 204
    remaining = client.get("/v1/mistakes", headers=headers).json()["items"]
    assert set(_by_question(remaining)) == {"q6"}


def test_mistake_hidden_from_other_user(client, wechat):
    wechat.openid_by_code["a"] = "openid-a"
    wechat.openid_by_code["b"] = "openid-b"
    headers_a = auth_header(client, code="a")
    headers_b = auth_header(client, code="b")
    client.post(
        "/v1/reports",
        headers=headers_a,
        json={"quiz": valid_quiz_payload(), "answers": sample_answers(wrong_first=True)},
    )
    mistake_id = client.get("/v1/mistakes", headers=headers_a).json()["items"][0]["id"]
    hidden = client.get(f"/v1/mistakes/{mistake_id}", headers=headers_b)
    assert hidden.status_code == 404
    assert hidden.json() == {"error": "not_found"}
    reviewed = client.post(
        f"/v1/mistakes/{mistake_id}/review",
        headers=headers_b,
        json={"optionId": "B"},
    )
    assert reviewed.status_code == 404
    deleted = client.delete(f"/v1/mistakes/{mistake_id}", headers=headers_b)
    assert deleted.status_code == 404
