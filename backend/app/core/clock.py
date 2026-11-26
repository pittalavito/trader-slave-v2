"""The app clock.

No module calls `datetime.now()`: they all receive a `Clock`.
In production it is the real clock (UTC); in backtests the engine moves time
forward candle by candle, so the same code behaves the same way.
"""

from datetime import UTC, datetime, timedelta
from typing import Protocol

from app.core.errors import ValidationError


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    """The real clock, always in UTC."""

    def now(self) -> datetime:
        return datetime.now(UTC)


class SimulatedClock:
    """Manually driven clock, for backtests and tests."""

    def __init__(self, start: datetime) -> None:
        self._now = _require_utc(start)

    def now(self) -> datetime:
        return self._now

    def set(self, moment: datetime) -> None:
        moment = _require_utc(moment)
        if moment < self._now:
            raise ValidationError("The simulated clock cannot go backwards", code="clock_backwards")
        self._now = moment

    def advance(self, delta: timedelta) -> None:
        self.set(self._now + delta)


def _require_utc(moment: datetime) -> datetime:
    if moment.tzinfo is None or moment.utcoffset() != timedelta(0):
        raise ValidationError("A UTC datetime is required", code="naive_or_non_utc_datetime")
    return moment
