from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.engine import Engine

from app.errors import BizError
from app.routers import auth, health, me, quizzes, records, reports


def create_app(*, engine: Engine | None = None) -> FastAPI:
    from app.config import get_settings
    from app.db import Base, make_engine, make_session_factory
    import app.models  # noqa: F401

    app = FastAPI(title="关卡学 API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:10086",
            "http://127.0.0.1:10086",
            "http://localhost:10087",
            "http://127.0.0.1:10087",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    bound = engine or make_engine(get_settings())
    app.state.engine = bound
    app.state.session_factory = make_session_factory(bound)
    Base.metadata.create_all(bind=bound)

    @app.exception_handler(BizError)
    async def biz_error_handler(_request: Request, exc: BizError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": exc.error})

    app.include_router(health.router, prefix="/v1")
    app.include_router(auth.router, prefix="/v1")
    app.include_router(me.router, prefix="/v1")
    app.include_router(records.router, prefix="/v1")
    app.include_router(quizzes.router, prefix="/v1")
    app.include_router(reports.router, prefix="/v1")
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    from app.config import get_settings

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.api_host or "127.0.0.1",
        port=settings.api_port or 8000,
        reload=True,
    )
