from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.errors import BizError
from app.routers import health, quizzes, reports


def create_app() -> FastAPI:
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

    @app.exception_handler(BizError)
    async def biz_error_handler(_request: Request, exc: BizError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": exc.error})

    app.include_router(health.router, prefix="/v1")
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

