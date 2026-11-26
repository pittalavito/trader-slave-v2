"""Client simulato per backtest, paper trading e test.

Esegue gli ordini al prezzo dell'ultima candela conosciuta, senza toccare
nessun conto. Commissioni e slittamento arrivano nella fase "Motore di backtest".
"""

from collections import defaultdict
from datetime import datetime

from app.core.clock import Clock
from app.core.errors import DomainError
from app.core.types import Symbol, Timeframe
from app.engine.models import Candle, OrderRequest, Position


class SimulatedClient:
    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._candles: dict[tuple[Symbol, Timeframe], list[Candle]] = defaultdict(list)
        self.open_positions: list[Position] = []

    def load_candles(self, timeframe: Timeframe, candles: list[Candle]) -> None:
        for candle in candles:
            self._candles[(candle.symbol, timeframe)].append(candle)

    async def fetch_candles(
        self, symbol: Symbol, timeframe: Timeframe, since: datetime | None = None, limit: int = 500
    ) -> list[Candle]:
        # Solo candele già "accadute" secondo l'orologio: niente sbirciate nel futuro.
        now = self._clock.now()
        visible = [
            c
            for c in self._candles[(symbol, timeframe)]
            if c.open_time <= now and (since is None or c.open_time >= since)
        ]
        return visible[-limit:]

    def _last_price(self, symbol: Symbol) -> Candle:
        now = self._clock.now()
        candidates = [
            c for (s, _), cs in self._candles.items() if s == symbol for c in cs if c.open_time <= now
        ]
        if not candidates:
            raise DomainError("Nessun prezzo disponibile per il simbolo", details={"symbol": str(symbol)})
        return max(candidates, key=lambda c: c.open_time)

    async def open_position(self, order: OrderRequest) -> Position:
        price = self._last_price(order.symbol).close
        position = Position(
            order.symbol, order.side, order.quantity, price, order.leverage, self._clock.now()
        )
        self.open_positions.append(position)
        return position

    async def close_position(self, position: Position) -> None:
        self.open_positions.remove(position)
