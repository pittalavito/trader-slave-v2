"""Data passed between the engine layers.

Immutable dataclasses (`frozen`, `slots`): fast in backtests and checked by mypy.
External data is validated earlier, at the edges, with Pydantic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from app.core.types import PortfolioId, Symbol, Timeframe


class Side(StrEnum):
    LONG = "long"
    SHORT = "short"


@dataclass(frozen=True, slots=True)
class Candle:
    symbol: Symbol
    open_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


@dataclass(frozen=True, slots=True)
class MarketData:
    symbol: Symbol
    timeframe: Timeframe
    candles: tuple[Candle, ...]

    @property
    def last_price(self) -> Decimal:
        return self.candles[-1].close


@dataclass(frozen=True, slots=True)
class Signal:
    """When to enter and in which direction. `side=None` means no signal."""

    symbol: Symbol
    side: Side | None
    reason: str = ""


@dataclass(frozen=True, slots=True)
class Position:
    symbol: Symbol
    side: Side
    quantity: Decimal
    entry_price: Decimal
    leverage: int
    opened_at: datetime


@dataclass(frozen=True, slots=True)
class PortfolioState:
    portfolio_id: PortfolioId
    capital: Decimal
    allocated_capital: Decimal = Decimal("0")
    all_time_high: Decimal = Decimal("0")
    open_positions: tuple[Position, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class RiskAssessment:
    can_open: bool
    reason: str = ""


@dataclass(frozen=True, slots=True)
class OrderRequest:
    symbol: Symbol
    side: Side
    quantity: Decimal
    leverage: int
