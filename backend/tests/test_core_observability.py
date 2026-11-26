import json

import pytest

from app.core.errors import DomainError
from app.core.observability import configure_observability, correlation_scope, observed


@observed
def add(a: int, b: int) -> int:
    return a + b


@observed(name="test.async_fail")
async def fail_async() -> None:
    raise DomainError("risk limit exceeded", code="risk_limit")


def _logs(captured: str) -> list[dict[str, object]]:
    return [json.loads(line) for line in captured.splitlines() if line.startswith("{")]


def test_observed_sync_logs_duration_and_correlation(capsys: pytest.CaptureFixture[str]) -> None:
    configure_observability(level="DEBUG")
    with correlation_scope("abc123"):
        assert add(2, 3) == 5
    (entry,) = [e for e in _logs(capsys.readouterr().out) if e.get("event") == "operation.ok"]
    assert entry["operation"] == "add"
    assert entry["outcome"] == "ok"
    assert entry["correlation_id"] == "abc123"
    assert isinstance(entry["duration_ms"], float)
    assert "trace_id" in entry


async def test_observed_async_logs_app_error_code(capsys: pytest.CaptureFixture[str]) -> None:
    configure_observability(level="DEBUG")
    with pytest.raises(DomainError):
        await fail_async()
    (entry,) = [e for e in _logs(capsys.readouterr().out) if e.get("event") == "operation.failed"]
    assert entry["operation"] == "test.async_fail"
    assert entry["error_code"] == "risk_limit"
    assert entry["level"] == "warning"


@observed(fields=["symbol"])
def place(symbol: str, api_key: str) -> str:
    return symbol


def test_observed_logs_only_chosen_fields(capsys: pytest.CaptureFixture[str]) -> None:
    configure_observability(level="DEBUG")
    place("BTC/USD", api_key="secret-key")
    (entry,) = [e for e in _logs(capsys.readouterr().out) if e.get("event") == "operation.ok"]
    assert entry["symbol"] == "BTC/USD"
    assert "api_key" not in entry
    assert "secret-key" not in json.dumps(entry)


def test_observed_rejects_unknown_fields() -> None:
    with pytest.raises(TypeError, match="unknown fields"):

        @observed(fields=["missing"])
        def noop() -> None: ...
