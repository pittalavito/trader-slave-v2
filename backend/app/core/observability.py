"""Logs, traces and the `@observed` decorator.

Three tools work together here:

- **structlog** writes the logs. Every log line is one JSON object, so it can be
  searched and filtered (e.g. "all errors of the Kraken client today").
- **OpenTelemetry** records *spans*: a span is "this function started at T and
  took N ms". Spans nest, so one engine cycle becomes a tree of steps
  (signal -> risk -> sizing -> execution) with the time spent in each.
  For now spans are only printed to the console when `OTEL_CONSOLE=true`;
  later they can be sent to a viewer (Grafana, Jaeger...) without code changes.
- **correlation id**: one id per API request or engine cycle, attached to every
  log line written inside it, so all the lines of one cycle can be found together.

How to use it:

- call `configure_observability()` once, when the API or the engine starts;
- put `@observed` on important methods (services, engine layers, clients);
- wrap a request or an engine cycle in `with correlation_scope():`.
"""

from __future__ import annotations

import functools
import inspect
import logging
import sys
import time
import uuid
from collections.abc import Awaitable, Callable, Generator, MutableMapping, Sequence
from contextlib import contextmanager
from typing import Any, cast, overload

import structlog
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.trace import Status, StatusCode

from app.core.errors import AppError

_TRACER_NAME = "trader_slave"

Logger = structlog.stdlib.BoundLogger


# --- Setup -----------------------------------------------------------------------------------------


def configure_observability(*, level: str = "INFO", json_logs: bool = True, otel_console: bool = False) -> None:
    """Configures structlog and OpenTelemetry. Safe to call more than once."""
    level = level.upper()
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level, force=True)

    renderer = structlog.processors.JSONRenderer() if json_logs else structlog.dev.ConsoleRenderer()
    structlog.configure(
        # Each log line goes through these steps, in order, before being printed.
        processors=[
            structlog.contextvars.merge_contextvars,  # adds correlation_id and other bound fields
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            _add_trace_ids,  # links the log line to the current span
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level)),
        cache_logger_on_first_use=False,
    )

    provider = TracerProvider()
    if otel_console:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)


def get_logger(name: str | None = None) -> Logger:
    return cast(Logger, structlog.get_logger(name))


def _add_trace_ids(_: Any, __: str, event: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    """structlog step: adds the ids of the current span, if there is one."""
    ctx = trace.get_current_span().get_span_context()
    if ctx.is_valid:
        event["trace_id"] = format(ctx.trace_id, "032x")
        event["span_id"] = format(ctx.span_id, "016x")
    return event


# --- Correlation id --------------------------------------------------------------------------------


@contextmanager
def correlation_scope(correlation_id: str | None = None, **extra: Any) -> Generator[str, None, None]:
    """Attaches an id (and any extra fields) to every log line written inside the block."""
    cid = correlation_id or uuid.uuid4().hex
    with structlog.contextvars.bound_contextvars(correlation_id=cid, **extra):
        yield cid


# --- @observed -------------------------------------------------------------------------------------


@overload
def observed[**P, R](func: Callable[P, R], /) -> Callable[P, R]: ...
@overload
def observed[**P, R](*, name: str | None = None, fields: Sequence[str] = ()) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


def observed[**P, R](
    func: Callable[P, R] | None = None, /, *, name: str | None = None, fields: Sequence[str] = ()
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Makes a function or method observable, sync or async.

    Each call opens a span and writes one log line with duration and outcome.
    `fields` lists the arguments to add to the log line and the span. Only the ones
    listed are written, so keys and passwords never end up in the logs by mistake.

    Usage: `@observed`, `@observed(name="kraken.fetch_candles")` or
    `@observed(fields=["symbol", "timeframe"])`.
    """

    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        operation = name or fn.__qualname__
        log = get_logger(fn.__module__)
        signature = inspect.signature(fn)
        unknown = set(fields) - set(signature.parameters)
        if unknown:
            raise TypeError(f"@observed on {operation}: unknown fields {sorted(unknown)}")

        def picked(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
            if not fields:
                return {}
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            return {field: bound.arguments[field] for field in fields}

        if inspect.iscoroutinefunction(fn):
            async_fn = cast(Callable[P, Awaitable[Any]], fn)

            @functools.wraps(fn)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                with _observe(operation, log, picked(args, kwargs)):
                    return await async_fn(*args, **kwargs)

            return cast(Callable[P, R], async_wrapper)

        @functools.wraps(fn)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with _observe(operation, log, picked(args, kwargs)):
                return fn(*args, **kwargs)

        return sync_wrapper

    return decorate(func) if func is not None else decorate


@contextmanager
def _observe(operation: str, log: Logger, extra: dict[str, Any]) -> Generator[None, None, None]:
    """The shared part of `@observed`: span, timing and the final log line."""
    with trace.get_tracer(_TRACER_NAME).start_as_current_span(operation) as span:
        for key, value in extra.items():
            span.set_attribute(f"arg.{key}", str(value))
        log = log.bind(**{key: str(value) for key, value in extra.items()})
        start = time.perf_counter()
        try:
            yield
        except Exception as exc:
            _log_failure(log, span, operation, _elapsed_ms(start), exc)
            raise
        log.debug("operation.ok", operation=operation, duration_ms=_elapsed_ms(start), outcome="ok")


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 3)


def _log_failure(log: Logger, span: trace.Span, operation: str, duration_ms: float, exc: Exception) -> None:
    span.record_exception(exc)
    span.set_status(Status(StatusCode.ERROR, str(exc)))
    fields: dict[str, Any] = {
        "operation": operation,
        "duration_ms": duration_ms,
        "outcome": "error",
        "error_type": type(exc).__name__,
    }
    if isinstance(exc, AppError):
        # Expected errors (AppError) are warnings; unexpected ones are errors with a stack trace.
        span.set_attribute("error.code", exc.code)
        log.warning("operation.failed", **fields, error_code=exc.code, error=exc.message)
    else:
        log.error("operation.failed", **fields, exc_info=exc)
