def test_health_ok(client, quiz_gen):
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert quiz_gen.calls == []
