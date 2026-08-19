from tests.conftest import auth_header


def test_me_requires_token(client):
    response = client.get("/v1/me")
    assert response.status_code == 401
    assert response.json() == {"error": "unauthorized"}


def test_me_rejects_bad_token(client):
    response = client.get("/v1/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert response.status_code == 401
    assert response.json() == {"error": "unauthorized"}


def test_me_ok(client):
    headers = auth_header(client)
    response = client.get("/v1/me", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["wechatConnected"] is True
    assert body["nickname"] is None


def test_update_me_nickname_and_avatar(client):
    headers = auth_header(client)
    response = client.put(
        "/v1/me",
        headers=headers,
        json={"nickname": "小关", "avatarUrl": "https://example.com/a.png"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["nickname"] == "小关"
    assert body["avatarUrl"] == "https://example.com/a.png"
    again = client.get("/v1/me", headers=headers).json()
    assert again["nickname"] == "小关"
