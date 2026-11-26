"""Kraken Futures tramite ccxt.

Per ora solo la lettura delle candele, che serve dalla fase "Dati di mercato".
Gli ordini arrivano nella fase "Soldi veri: strategia B su Kraken".
"""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import ccxt.async_support as ccxt

from app.core.errors import ExternalServiceError
from app.core.observability import observed
from app.core.types import Symbol, Timeframe
from app.engine.models import Candle


class KrakenFuturesClient:
    def __init__(self, exchange: Any | None = None) -> None:
        # L'exchange si può passare dall'esterno (nei test, un finto exchange).
        self._exchange = exchange or ccxt.krakenfutures({"enableRateLimit": True})

    @staticmethod
    def market_symbol(symbol: Symbol) -> str:
        """Simbolo ccxt dei perpetui lineari, per esempio BTC/USD:USD."""
        return f"{symbol.base}/{symbol.quote}:{symbol.quote}"

    @observed(name="kraken.fetch_candles")
    async def fetch_candles(
        self, symbol: Symbol, timeframe: Timeframe, since: datetime | None = None, limit: int = 500
    ) -> list[Candle]:
        since_ms = int(since.timestamp() * 1000) if since else None
        try:
            rows = await self._exchange.fetch_ohlcv(
                self.market_symbol(symbol), timeframe.value, since=since_ms, limit=limit
            )
        except ccxt.BaseError as exc:
            raise ExternalServiceError(
                "Kraken non ha restituito le candele", code="kraken_error", details={"reason": str(exc)}
            ) from exc
        return [_to_candle(symbol, row) for row in rows]

    async def close(self) -> None:
        await self._exchange.close()


def _to_candle(symbol: Symbol, row: list[Any]) -> Candle:
    ts, o, h, low, c, v = row[:6]
    # str() prima di Decimal: evita di portarsi dietro gli errori di arrotondamento dei float.
    return Candle(
        symbol=symbol,
        open_time=datetime.fromtimestamp(ts / 1000, tz=UTC),
        open=Decimal(str(o)),
        high=Decimal(str(h)),
        low=Decimal(str(low)),
        close=Decimal(str(c)),
        volume=Decimal(str(v or 0)),
    )
