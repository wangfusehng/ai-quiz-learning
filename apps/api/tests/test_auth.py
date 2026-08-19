from tests.conftest import auth_header


def test_wechat_login_returns_jwt_and_user(client):
    response = client.post("/v1/auth/wechat", json={"code": "wx-code"})
    assert response.status_code == 200
    body = response.json()
    assert body["token"]
    assert body["user"]["id"] >= 1
    assert body["user"]["nickname"] is None
    assert body["user"]["avatarUrl"] is None
    assert body["user"]["wechatConnected"] is True


def test_same_openid_returns_same_user(client):
    first = client.post("/v1/auth/wechat", json={"code": "a"}).json()
    second = client.post("/v1/auth/wechat", json={"code": "b"}).json()
    assert first["user"]["id"] == second["user"]["id"]
    assert first["token"] != second["token"]


def test_wechat_login_upstream(client, wechat):
    wechat.fail = True
    response = client.post("/v1/auth/wechat", json={"code": "wx-code"})
    assert response.status_code == 502
    assert response.json() == {"error": "upstream"}


def test_wechat_login_rejects_empty_code(client):
    response = client.post("/v1/auth/wechat", json={"code": ""})
    assert response.status_code == 422
