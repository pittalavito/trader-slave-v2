"""Kraken Futures through ccxt.

For now only candle reads, needed from the "Market data" phase.
Orders arrive in the "Real money: strategy B on Kraken" phase.
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
        # The exchange can be injected (a fake one in tests).
        self._exchange = exchange or ccxt.krakenfutures({"enableRateLimit": True})

    @staticmethod
    def market_symbol(symbol: Symbol) -> str:
        """ccxt symbol of the linear perpetual, e.g. BTC/USD:USD."""
        return f"{symbol.base}/{symbol.quote}:{symbol.quote}"

    @observed(name="kraken.fetch_candles", fields=["symbol", "timeframe"])
    async def fetch_candles(self, symbol: Symbol, timeframe: Timeframe, since: datetime | None = None, limit: int = 500) -> list[Candle]:
        since_ms = int(since.timestamp() * 1000) if since else None
        try:
            rows = await self._exchange.fetch_ohlcv(self.market_symbol(symbol), timeframe.value, since=since_ms, limit=limit)
        except ccxt.BaseError as exc:
            raise ExternalServiceError("Kraken did not return the candles", code="kraken_error", details={"reason": str(exc)}) from exc
        return [_to_candle(symbol, row) for row in rows]

    async def close(self) -> None:
        await self._exchange.close()


def _to_candle(symbol: Symbol, row: list[Any]) -> Candle:
    ts, o, h, low, c, v = row[:6]
    # str() before Decimal: avoids carrying float rounding errors over.
    return Candle(
        symbol=symbol,
        open_time=datetime.fromtimestamp(ts / 1000, tz=UTC),
        open=Decimal(str(o)),
        high=Decimal(str(h)),
        low=Decimal(str(low)),
        close=Decimal(str(c)),
        volume=Decimal(str(v or 0)),
    )
