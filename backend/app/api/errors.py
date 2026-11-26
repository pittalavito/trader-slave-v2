"""Turns app exceptions into HTTP responses, in a single place."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.errors import AppError
from app.core.observability import get_logger

log = get_logger(__name__)


async def _app_error_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)
    return JSONResponse(status_code=exc.status_code, content={"error": exc.to_dict()})


async def _unexpected_error_handler(_: Request, exc: Exception) -> JSONResponse:
    log.error("api.unexpected_error", exc_info=exc)
    body = {"error": {"code": "internal_error", "message": "Internal error", "details": {}}}
    return JSONResponse(status_code=500, content=body)


def install_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error_handler)
    app.add_exception_handler(Exception, _unexpected_error_handler)
