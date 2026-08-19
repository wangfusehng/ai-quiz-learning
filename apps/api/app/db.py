from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import Settings

_API_DIR = Path(__file__).resolve().parent.parent


class Base(DeclarativeBase):
    pass


def database_url(settings: Settings) -> str:
    if settings.database_url:
        return settings.database_url
    if settings.mysql_host and settings.mysql_user and settings.mysql_database:
        user = quote_plus(settings.mysql_user)
        password = quote_plus(settings.mysql_password)
        return (
            f"mysql+pymysql://{user}:{password}"
            f"@{settings.mysql_host}:{settings.mysql_port}/"
            f"{settings.mysql_database}?charset=utf8mb4"
        )
    path = (_API_DIR / "data" / "dev.sqlite").resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path.as_posix()}"


def make_engine(settings: Settings) -> Engine:
    url = database_url(settings)
    kwargs: dict = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(url, **kwargs)


def make_session_factory(engine: Engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
