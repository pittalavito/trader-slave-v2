from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.core.clock import SimulatedClock, SystemClock
from app.core.errors import ValidationError

START = datetime(2026, 1, 1, tzinfo=UTC)


def test_system_clock_is_utc() -> None:
    assert SystemClock().now().utcoffset() == timedelta(0)


def test_simulated_clock_advances() -> None:
    clock = SimulatedClock(START)
    clock.advance(timedelta(minutes=5))
    assert clock.now() == START + timedelta(minutes=5)


def test_simulated_clock_never_goes_back() -> None:
    clock = SimulatedClock(START)
    with pytest.raises(ValidationError):
        clock.set(START - timedelta(seconds=1))


def test_simulated_clock_requires_utc() -> None:
    with pytest.raises(ValidationError):
        SimulatedClock(datetime(2026, 1, 1))  # noqa: DTZ001
    with pytest.raises(ValidationError):
        SimulatedClock(datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=1))))
