"""I sei livelli del motore, ripresi dal vecchio trader-slave.

Ogni strategia implementa solo `SignalLayer`. Rischio, dimensionamento,
esecuzione e portafoglio sono comuni a tutte le strategie.
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
    """Fornisce le candele del timeframe scelto."""

    @abstractmethod
    async def get(self, symbol: Symbol, timeframe: Timeframe) -> MarketData: ...


class SignalLayer(ABC):
    """La strategia: decide quando entrare e in che direzione."""

    name: str

    @abstractmethod
    async def generate(self, market: MarketData) -> Signal: ...

    async def should_close(self, position: Position, market: MarketData) -> bool:
        """Se chiudere una posizione aperta. Di default non chiude mai."""
        return False


class RiskLayer(ABC):
    """Decide se si può aprire una nuova posizione."""

    @abstractmethod
    async def assess(self, portfolio: PortfolioState, market: MarketData) -> RiskAssessment: ...


class SizingLayer(ABC):
    """Decide quanto investire e con quale leva."""

    @abstractmethod
    async def size(
        self, signal: Signal, portfolio: PortfolioState, market: MarketData
    ) -> OrderRequest | None: ...


class ExecutionLayer(ABC):
    """Manda l'ordine: in backtest, in simulazione o sul conto reale."""

    @abstractmethod
    async def open(self, order: OrderRequest, price_hint: MarketData) -> Position: ...

    @abstractmethod
    async def close(self, position: Position, price_hint: MarketData) -> None: ...


class PortfolioLayer(ABC):
    """Tiene capitale, capitale impegnato, massimo storico e posizioni aperte."""

    @abstractmethod
    async def get(self, portfolio_id: PortfolioId) -> PortfolioState: ...

    @abstractmethod
    async def record_open(self, portfolio_id: PortfolioId, position: Position) -> None: ...

    @abstractmethod
    async def record_close(
        self, portfolio_id: PortfolioId, position: Position, exit_price_hint: MarketData
    ) -> None: ...
