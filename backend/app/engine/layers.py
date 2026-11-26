"""I sei livelli del motore, ripresi dal vecchio trader-slave.

Ogni strategia implementa solo `SignalLayer`. Rischio, dimensionamento,
esecuzione e portafoglio sono comuni a tutte le strategie.
"""

from abc import ABC, abstractmethod

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
    def get(self, symbol: str, timeframe: str) -> MarketData: ...


class SignalLayer(ABC):
    """La strategia: decide quando entrare e in che direzione."""

    name: str

    @abstractmethod
    def generate(self, market: MarketData) -> Signal: ...

    def should_close(self, position: Position, market: MarketData) -> bool:
        """Se chiudere una posizione aperta. Di default non chiude mai."""
        return False


class RiskLayer(ABC):
    """Decide se si può aprire una nuova posizione."""

    @abstractmethod
    def assess(self, portfolio: PortfolioState, market: MarketData) -> RiskAssessment: ...


class SizingLayer(ABC):
    """Decide quanto investire e con quale leva."""

    @abstractmethod
    def size(self, signal: Signal, portfolio: PortfolioState, market: MarketData) -> OrderRequest | None: ...


class ExecutionLayer(ABC):
    """Manda l'ordine: in backtest, in simulazione o sul conto reale."""

    @abstractmethod
    def open(self, order: OrderRequest, price_hint: MarketData) -> Position: ...

    @abstractmethod
    def close(self, position: Position, price_hint: MarketData) -> None: ...


class PortfolioLayer(ABC):
    """Tiene capitale, capitale impegnato, massimo storico e posizioni aperte."""

    @abstractmethod
    def get(self, portfolio_id: int) -> PortfolioState: ...

    @abstractmethod
    def record_open(self, portfolio_id: int, position: Position) -> None: ...

    @abstractmethod
    def record_close(self, portfolio_id: int, position: Position, exit_price_hint: MarketData) -> None: ...
