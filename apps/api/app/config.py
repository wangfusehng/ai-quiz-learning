from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_API_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_API_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-v4-flash"
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    wechat_app_id: str = Field(default="", validation_alias=AliasChoices("WECHAT_APP_ID", "AppID"))
    wechat_app_secret: str = Field(
        default="",
        validation_alias=AliasChoices("WECHAT_APP_SECRET", "AppSecret"),
    )
    jwt_secret: str = Field(default="dev-change-me")
    jwt_expire_days: int = 30
    mysql_host: str = ""
    mysql_port: int = 3306
    mysql_user: str = ""
    mysql_password: str = ""
    mysql_database: str = ""
    database_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
