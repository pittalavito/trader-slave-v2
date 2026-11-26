"""Shared client interfaces."""

from datetime import datetime
from typing import Protocol

from app.core.types import Symbol, Timeframe
from app.engine.models import Candle, OrderRequest, Position


class MarketDataClient(Protocol):
    """Provides the candles of a market."""

    async def fetch_candles(
        self, symbol: Symbol, timeframe: Timeframe, since: datetime | None = None, limit: int = 500
    ) -> list[Candle]: ...


class TradingClient(Protocol):
    """Opens and closes positions on an account."""

    async def open_position(self, order: OrderRequest) -> Position: ...

    async def close_position(self, position: Position) -> None: ...
