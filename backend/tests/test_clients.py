from datetime import timedelta
from decimal import Decimal
from typing import Any

import ccxt.async_support as ccxt
import pytest

from app.clients.kraken.client import KrakenFuturesClient
from app.clients.simulated.client import SimulatedClient
from app.core.clock import SimulatedClock
from app.core.errors import ExternalServiceError
from app.core.types import Symbol, Timeframe
from app.engine.models import Candle, OrderRequest, Side
from tests.conftest import START

BTC = Symbol("BTC", "USD")


class FakeExchange:
    def __init__(self, rows: list[list[Any]] | None = None, error: Exception | None = None) -> None:
        self.rows = rows or []
        self.error = error
        self.calls: list[tuple[str, str]] = []

    async def fetch_ohlcv(self, symbol: str, timeframe: str, since: int | None, limit: int) -> list[list[Any]]:
        self.calls.append((symbol, timeframe))
        if self.error:
            raise self.error
        return self.rows

    async def close(self) -> None:
        pass


async def test_kraken_maps_ohlcv_to_decimal_candles() -> None:
    ts = int(START.timestamp() * 1000)
    fake = FakeExchange([[ts, 100.1, 101.2, 99.3, 100.4, 12.5]])
    candles = await KrakenFuturesClient(fake).fetch_candles(BTC, Timeframe.M5)
    assert fake.calls == [("BTC/USD:USD", "5m")]
    assert candles == [Candle(BTC, START, Decimal("100.1"), Decimal("101.2"), Decimal("99.3"), Decimal("100.4"), Decimal("12.5"))]


async def test_kraken_errors_become_external_service_errors() -> None:
    fake = FakeExchange(error=ccxt.NetworkError("timeout"))
    with pytest.raises(ExternalServiceError) as err:
        await KrakenFuturesClient(fake).fetch_candles(BTC, Timeframe.M1)
    assert err.value.code == "kraken_error"


def _candle(minutes: int, price: str) -> Candle:
    p = Decimal(price)
    return Candle(BTC, START + timedelta(minutes=minutes), p, p, p, p, Decimal("1"))


async def test_simulated_client_never_shows_the_future() -> None:
    clock = SimulatedClock(START)
    client = SimulatedClient(clock)
    client.load_candles(Timeframe.M1, [_candle(0, "100"), _candle(1, "101"), _candle(2, "102")])

    assert [c.close for c in await client.fetch_candles(BTC, Timeframe.M1)] == [Decimal("100")]
    clock.advance(timedelta(minutes=2))
    assert len(await client.fetch_candles(BTC, Timeframe.M1)) == 3

    position = await client.open_position(OrderRequest(BTC, Side.LONG, Decimal("1"), leverage=2))
    assert position.entry_price == Decimal("102")
    assert position.opened_at == clock.now()
