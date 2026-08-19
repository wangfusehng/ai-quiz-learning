from app.config import get_settings


def test_settings_read_appid_alias(monkeypatch):
    monkeypatch.setenv("AppID", "wxTESTAPPID")
    monkeypatch.setenv("AppSecret", "test-secret")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.wechat_app_id == "wxTESTAPPID"
    assert settings.wechat_app_secret == "test-secret"
    get_settings.cache_clear()
