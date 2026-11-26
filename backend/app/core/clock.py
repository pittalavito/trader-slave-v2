"""L'orologio dell'app.

Nessun modulo chiama `datetime.now()`: tutti ricevono un `Clock`.
In produzione è l'orologio vero (UTC); nel backtest è il motore a far
avanzare il tempo candela per candela, così lo stesso codice gira uguale.
"""

from datetime import UTC, datetime, timedelta
from typing import Protocol

from app.core.errors import ValidationError


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    """L'orologio vero, sempre in UTC."""

    def now(self) -> datetime:
        return datetime.now(UTC)


class SimulatedClock:
    """Orologio controllato a mano, per backtest e test."""

    def __init__(self, start: datetime) -> None:
        self._now = _require_utc(start)

    def now(self) -> datetime:
        return self._now

    def set(self, moment: datetime) -> None:
        moment = _require_utc(moment)
        if moment < self._now:
            raise ValidationError("L'orologio simulato non può tornare indietro", code="clock_backwards")
        self._now = moment

    def advance(self, delta: timedelta) -> None:
        self.set(self._now + delta)


def _require_utc(moment: datetime) -> datetime:
    if moment.tzinfo is None or moment.utcoffset() != timedelta(0):
        raise ValidationError("Serve una data in UTC", code="naive_or_non_utc_datetime")
    return moment
