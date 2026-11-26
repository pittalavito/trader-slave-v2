"""Log, tracce e il decoratore `@observed`.

- `configure_observability()` va chiamato una volta all'avvio di API e motore.
- `@observed` si mette sui metodi importanti: registra durata, esito ed errori
  sia nei log (JSON, con structlog) sia come traccia OpenTelemetry.
- `correlation_scope()` assegna un id a una richiesta o a un ciclo del motore:
  tutti i log al suo interno lo riportano, così si ricostruisce cosa è successo.
"""

from __future__ import annotations

import functools
import inspect
import logging
import sys
import time
import uuid
from collections.abc import Awaitable, Callable, Iterator, MutableMapping
from contextlib import contextmanager
from typing import Any, cast, overload

import structlog
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.trace import Status, StatusCode

from app.core.errors import AppError

_TRACER_NAME = "trader_slave"


def configure_observability(
    *, level: str = "INFO", json_logs: bool = True, otel_console: bool = False
) -> None:
    """Imposta structlog e OpenTelemetry. Si può chiamare più volte senza danni."""
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level.upper(), force=True)
    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer() if json_logs else structlog.dev.ConsoleRenderer()
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            _add_trace_ids,
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level.upper())),
        cache_logger_on_first_use=False,
    )
    provider = TracerProvider()
    if otel_console:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))


def _add_trace_ids(_: Any, __: str, event: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    ctx = trace.get_current_span().get_span_context()
    if ctx.is_valid:
        event["trace_id"] = format(ctx.trace_id, "032x")
        event["span_id"] = format(ctx.span_id, "016x")
    return event


@contextmanager
def correlation_scope(correlation_id: str | None = None, **extra: Any) -> Iterator[str]:
    """Lega un id (e altri campi) a tutti i log emessi dentro il blocco."""
    cid = correlation_id or uuid.uuid4().hex
    with structlog.contextvars.bound_contextvars(correlation_id=cid, **extra):
        yield cid


@overload
def observed[**P, R](func: Callable[P, R], /) -> Callable[P, R]: ...
@overload
def observed[**P, R](*, name: str | None = None) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


def observed[**P, R](
    func: Callable[P, R] | None = None, /, *, name: str | None = None
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Rende osservabile una funzione o un metodo, sincrono o asincrono.

    Uso: `@observed` oppure `@observed(name="kraken.fetch_candles")`.
    """

    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        span_name = name or fn.__qualname__
        log = get_logger(fn.__module__)

        if inspect.iscoroutinefunction(fn):
            async_fn = cast(Callable[P, Awaitable[Any]], fn)

            @functools.wraps(fn)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                tracer = trace.get_tracer(_TRACER_NAME)
                with tracer.start_as_current_span(span_name) as span:
                    start = time.perf_counter()
                    try:
                        result = await async_fn(*args, **kwargs)
                    except Exception as exc:
                        _record_failure(log, span, span_name, start, exc)
                        raise
                    _record_success(log, span_name, start)
                    return result

            return cast(Callable[P, R], async_wrapper)

        @functools.wraps(fn)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            tracer = trace.get_tracer(_TRACER_NAME)
            with tracer.start_as_current_span(span_name) as span:
                start = time.perf_counter()
                try:
                    result = fn(*args, **kwargs)
                except Exception as exc:
                    _record_failure(log, span, span_name, start, exc)
                    raise
                _record_success(log, span_name, start)
                return result

        return sync_wrapper

    if func is not None:
        return decorate(func)
    return decorate


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 3)


def _record_success(log: structlog.stdlib.BoundLogger, op: str, start: float) -> None:
    log.debug("operation.ok", operation=op, duration_ms=_elapsed_ms(start), outcome="ok")


def _record_failure(
    log: structlog.stdlib.BoundLogger, span: trace.Span, op: str, start: float, exc: Exception
) -> None:
    span.record_exception(exc)
    span.set_status(Status(StatusCode.ERROR, str(exc)))
    fields: dict[str, Any] = {
        "operation": op,
        "duration_ms": _elapsed_ms(start),
        "outcome": "error",
        "error_type": type(exc).__name__,
    }
    if isinstance(exc, AppError):
        fields["error_code"] = exc.code
        span.set_attribute("error.code", exc.code)
        # Gli errori previsti sono avvisi; quelli inattesi sono errori con stack trace.
        log.warning("operation.failed", **fields, error=exc.message)
    else:
        log.error("operation.failed", **fields, exc_info=exc)
