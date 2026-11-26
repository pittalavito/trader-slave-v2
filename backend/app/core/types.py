"""Tipi comuni a tutto il backend.

Servono a far fermare a mypy errori che con tipi generici passerebbero:
sommare euro e dollari, passare l'id di un utente dove serve quello di un
portafoglio, scrivere un timeframe inesistente.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import NewType

from app.core.errors import DomainError, ValidationError

# Id distinti per entità: per mypy un UserId non è un PortfolioId.
UserId = NewType("UserId", int)
PortfolioId = NewType("PortfolioId", int)
StrategyId = NewType("StrategyId", int)
CommandId = NewType("CommandId", int)


@dataclass(frozen=True, slots=True)
class Money:
    """Un importo con la sua valuta. Mai float: sempre Decimal."""

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise ValidationError("L'importo deve essere un Decimal", code="money_not_decimal")
        if not self.currency or self.currency != self.currency.upper():
            raise ValidationError(
                "Valuta non valida", code="invalid_currency", details={"currency": self.currency}
            )

    @classmethod
    def zero(cls, currency: str) -> Money:
        return cls(Decimal("0"), currency)

    def _same_currency(self, other: Money) -> None:
        if other.currency != self.currency:
            raise DomainError(
                "Non si possono combinare valute diverse",
                code="currency_mismatch",
                details={"left": self.currency, "right": other.currency},
            )

    def __add__(self, other: Money) -> Money:
        self._same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Decimal | int) -> Money:
        if isinstance(factor, float):
            raise ValidationError("Niente float con i soldi", code="money_float_factor")
        return Money(self.amount * Decimal(factor), self.currency)

    def __neg__(self) -> Money:
        return Money(-self.amount, self.currency)

    def __lt__(self, other: Money) -> bool:
        self._same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: Money) -> bool:
        self._same_currency(other)
        return self.amount <= other.amount

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"


@dataclass(frozen=True, slots=True)
class Symbol:
    """Una coppia di trading, per esempio SOL/USDC o BTC/USD."""

    base: str
    quote: str

    @classmethod
    def parse(cls, value: str) -> Symbol:
        parts = value.upper().split("/")
        if len(parts) != 2 or not all(parts):
            raise ValidationError("Simbolo non valido, serve la forma BASE/QUOTE", details={"symbol": value})
        return cls(parts[0], parts[1])

    def __str__(self) -> str:
        return f"{self.base}/{self.quote}"


class TimeframeBlock(StrEnum):
    """I tre blocchi di timeframe della specifica funzionale."""

    FAST = "fast"  # 1-3 minuti
    MEDIUM = "medium"  # 5-30 minuti
    SLOW = "slow"  # da 1 ora a 1 giorno


class Timeframe(StrEnum):
    M1 = "1m"
    M3 = "3m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"

    @property
    def seconds(self) -> int:
        unit = {"m": 60, "h": 3600, "d": 86400}[self.value[-1]]
        return int(self.value[:-1]) * unit

    @property
    def block(self) -> TimeframeBlock:
        if self.seconds <= 3 * 60:
            return TimeframeBlock.FAST
        if self.seconds <= 30 * 60:
            return TimeframeBlock.MEDIUM
        return TimeframeBlock.SLOW
