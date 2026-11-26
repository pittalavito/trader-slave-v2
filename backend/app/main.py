"""API entry point."""

from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response

from app.api.errors import install_error_handlers
from app.api.health import router as health_router
from app.core.config import Settings, get_settings
from app.core.container import Container, build_container
from app.core.observability import configure_observability, correlation_scope


def create_app(settings: Settings | None = None, container: Container | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        configure_observability(level=settings.log_level, json_logs=settings.is_production, otel_console=settings.otel_console)
        app.state.container = container or build_container(settings)
        yield
        await app.state.container.close()

    app = FastAPI(title="Trader Slave API", version="0.1.0", lifespan=lifespan)
    install_error_handlers(app)

    @app.middleware("http")
    async def correlation_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        with correlation_scope(request.headers.get("x-request-id"), path=request.url.path) as cid:
            response = await call_next(request)
        response.headers["x-request-id"] = cid
        return response

    app.include_router(health_router)
    return app


app = create_app()
