"""Точка входа: сборка маршрутов по заданиям ТЗ (разделы 6–8)."""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette import status

from app.config import get_settings
from app.database import init_db
from app.rate_limit import limiter
from app.tasks import task_6_1_api
from app.tasks import task_6_2_api
from app.tasks import task_6_4_api
from app.tasks import task_6_4_protected
from app.tasks import task_6_5
from app.tasks import task_7_1
from app.tasks import task_8_1
from app.tasks import task_8_2
from app.tasks.task_6_3 import verify_docs_basic


def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too many requests"},
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    task = settings.app_task
    app = FastAPI(
        title="FAPI KR3",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

    @app.middleware("http")
    async def prod_docs_block(request: Request, call_next):
        if get_settings().mode == "PROD":
            p = request.url.path
            if p in ("/docs", "/openapi.json", "/redoc") or p.startswith("/docs"):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"detail": "Not Found"},
                )
        return await call_next(request)

    if task == "6.1":
        app.include_router(task_6_1_api.router)
    elif task == "6.2":
        app.include_router(task_6_2_api.router)
    elif task == "6.3":
        app.include_router(task_6_2_api.router)
    elif task == "6.4":
        app.include_router(task_6_4_api.router)
        app.include_router(task_6_4_protected.router)
    elif task == "6.5":
        app.include_router(task_6_5.router)
        app.include_router(task_6_4_protected.router)
    elif task == "7.1":
        app.include_router(task_6_5.router)
        app.include_router(task_7_1.rbac_router)
    elif task == "8.1":
        app.include_router(task_8_1.router)
    elif task == "8.2":
        app.include_router(task_8_2.router)

    if task == "6.3" and settings.mode == "DEV":

        @app.get(
            "/openapi.json",
            include_in_schema=False,
            dependencies=[Depends(verify_docs_basic)],
        )
        async def openapi_json():
            return JSONResponse(app.openapi())

        @app.get(
            "/docs",
            include_in_schema=False,
            dependencies=[Depends(verify_docs_basic)],
        )
        async def swagger_docs():
            return get_swagger_ui_html(
                openapi_url="/openapi.json",
                title=f"{app.title} – Swagger UI",
            )

    @app.get("/")
    def root() -> dict:
        return {"status": "ok", "mode": get_settings().mode, "task": task}

    return app


app = create_app()
