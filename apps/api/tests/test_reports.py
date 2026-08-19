from tests.fixtures import sample_answers, valid_quiz_payload


def test_create_report_ok(client, report_gen):
    response = client.post(
        "/v1/reports",
        json={"quiz": valid_quiz_payload(), "answers": sample_answers(wrong_first=True)},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["aiGenerated"] is True
    assert body["quizId"] == "quiz-fixture-1"
    # 6 道选择：q1 错、q6 错 → 对 4 道。服务端覆盖模型分数。
    assert body["scoreHint"]["correct"] == 4
    assert body["scoreHint"]["total"] == 6
    assert report_gen.calls


def test_create_report_rejects_mismatched_quiz_id(client, report_gen):
    answers = sample_answers()
    answers["quizId"] = "other"
    response = client.post(
        "/v1/reports",
        json={"quiz": valid_quiz_payload(), "answers": answers},
    )
    assert response.status_code == 422
    assert response.json() == {"error": "quiz_invalid"}
    assert report_gen.calls == []


def test_create_report_upstream(client, report_gen):
    from app.errors import UpstreamError

    report_gen.error = UpstreamError("timeout")
    response = client.post(
        "/v1/reports",
        json={"quiz": valid_quiz_payload(), "answers": sample_answers()},
    )
    assert response.status_code == 502
    assert response.json() == {"error": "upstream"}
