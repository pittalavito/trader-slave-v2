"""The six engine layers, taken from the old trader-slave.

Each strategy only implements `SignalLayer`. Risk, sizing, execution and
portfolio are shared by all strategies.
"""

from abc import ABC, abstractmethod

from app.core.types import PortfolioId, Symbol, Timeframe
from app.engine.models import (
    MarketData,
    OrderRequest,
    PortfolioState,
    Position,
    RiskAssessment,
    Signal,
)


class MarketDataLayer(ABC):
    """Provides candles for the chosen timeframe."""

    @abstractmethod
    async def get(self, symbol: Symbol, timeframe: Timeframe) -> MarketData: ...


class SignalLayer(ABC):
    """The strategy: decides when to enter and in which direction."""

    name: str

    @abstractmethod
    async def generate(self, market: MarketData) -> Signal: ...

    async def should_close(self, position: Position, market: MarketData) -> bool:
        """Whether to close an open position. Never closes by default."""
        return False


class RiskLayer(ABC):
    """Decides whether a new position may be opened."""

    @abstractmethod
    async def assess(self, portfolio: PortfolioState, market: MarketData) -> RiskAssessment: ...


class SizingLayer(ABC):
    """Decides how much to invest and with which leverage."""

    @abstractmethod
    async def size(self, signal: Signal, portfolio: PortfolioState, market: MarketData) -> OrderRequest | None: ...


class ExecutionLayer(ABC):
    """Sends the order: in backtest, in simulation or on the real account."""

    @abstractmethod
    async def open(self, order: OrderRequest, price_hint: MarketData) -> Position: ...

    @abstractmethod
    async def close(self, position: Position, price_hint: MarketData) -> None: ...


class PortfolioLayer(ABC):
    """Tracks capital, allocated capital, all-time high and open positions."""

    @abstractmethod
    async def get(self, portfolio_id: PortfolioId) -> PortfolioState: ...

    @abstractmethod
    async def record_open(self, portfolio_id: PortfolioId, position: Position) -> None: ...

    @abstractmethod
    async def record_close(self, portfolio_id: PortfolioId, position: Position, exit_price_hint: MarketData) -> None: ...
