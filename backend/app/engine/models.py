"""Dati che passano tra i livelli del motore."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum


class Side(str, Enum):
    LONG = "long"
    SHORT = "short"


class TimeframeBlock(str, Enum):
    """I tre blocchi di timeframe della specifica funzionale."""

    FAST = "fast"  # 1-3 minuti
    MEDIUM = "medium"  # 5-30 minuti
    SLOW = "slow"  # da 1 ora a 1 giorno


@dataclass(frozen=True)
class Candle:
    symbol: str
    open_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


@dataclass(frozen=True)
class MarketData:
    symbol: str
    timeframe: str
    candles: list[Candle]

    @property
    def last_price(self) -> Decimal:
        return self.candles[-1].close


@dataclass(frozen=True)
class Signal:
    """Quando entrare e in che direzione. `side=None` significa nessun segnale."""

    symbol: str
    side: Side | None
    reason: str = ""


@dataclass
class Position:
    symbol: str
    side: Side
    quantity: Decimal
    entry_price: Decimal
    leverage: int
    opened_at: datetime


@dataclass
class PortfolioState:
    portfolio_id: int
    capital: Decimal
    allocated_capital: Decimal = Decimal("0")
    all_time_high: Decimal = Decimal("0")
    open_positions: list[Position] = field(default_factory=list)


@dataclass(frozen=True)
class RiskAssessment:
    can_open: bool
    reason: str = ""


@dataclass(frozen=True)
class OrderRequest:
    symbol: str
    side: Side
    quantity: Decimal
    leverage: int
