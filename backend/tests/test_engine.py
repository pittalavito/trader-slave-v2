from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal

from app.core.types import PortfolioId, Symbol, Timeframe
from app.engine.engine import BotConfig, Engine
from app.engine.layers import (
    ExecutionLayer,
    MarketDataLayer,
    PortfolioLayer,
    RiskLayer,
    SignalLayer,
    SizingLayer,
)
from app.engine.models import (
    Candle,
    MarketData,
    OrderRequest,
    PortfolioState,
    Position,
    RiskAssessment,
    Side,
    Signal,
)

NOW = datetime(2026, 1, 1, tzinfo=UTC)
SOL = Symbol("SOL", "USDC")


class FixedMarket(MarketDataLayer):
    async def get(self, symbol: Symbol, timeframe: Timeframe) -> MarketData:
        price = Decimal("100")
        candle = Candle(symbol, NOW, price, price, price, price, Decimal("1"))
        return MarketData(symbol, timeframe, (candle,))


class FixedSignal(SignalLayer):
    name = "fixed"

    def __init__(self, side: Side | None, close: bool = False) -> None:
        self.side = side
        self.close = close

    async def generate(self, market: MarketData) -> Signal:
        return Signal(market.symbol, self.side)

    async def should_close(self, position: Position, market: MarketData) -> bool:
        return self.close


class FixedRisk(RiskLayer):
    def __init__(self, can_open: bool) -> None:
        self.can_open = can_open

    async def assess(self, portfolio: PortfolioState, market: MarketData) -> RiskAssessment:
        return RiskAssessment(self.can_open)


class OneUnitSizing(SizingLayer):
    async def size(self, signal: Signal, portfolio: PortfolioState, market: MarketData) -> OrderRequest | None:
        assert signal.side is not None
        return OrderRequest(signal.symbol, signal.side, Decimal("1"), leverage=2)


class PaperExecution(ExecutionLayer):
    async def open(self, order: OrderRequest, price_hint: MarketData) -> Position:
        return Position(order.symbol, order.side, order.quantity, price_hint.last_price, order.leverage, NOW)

    async def close(self, position: Position, price_hint: MarketData) -> None:
        pass


class MemoryPortfolio(PortfolioLayer):
    def __init__(self) -> None:
        self.state = PortfolioState(portfolio_id=PortfolioId(1), capital=Decimal("1000"))

    async def get(self, portfolio_id: PortfolioId) -> PortfolioState:
        return self.state

    async def record_open(self, portfolio_id: PortfolioId, position: Position) -> None:
        self.state = replace(self.state, open_positions=(*self.state.open_positions, position))

    async def record_close(self, portfolio_id: PortfolioId, position: Position, exit_price_hint: MarketData) -> None:
        remaining = tuple(p for p in self.state.open_positions if p != position)
        self.state = replace(self.state, open_positions=remaining)


def make_engine(signal: SignalLayer, can_open: bool = True) -> tuple[Engine, MemoryPortfolio]:
    portfolio = MemoryPortfolio()
    engine = Engine(
        config=BotConfig(portfolio_id=PortfolioId(1), symbol=SOL, timeframe=Timeframe.M5),
        market_data=FixedMarket(),
        signal=signal,
        risk=FixedRisk(can_open),
        sizing=OneUnitSizing(),
        execution=PaperExecution(),
        portfolio=portfolio,
    )
    return engine, portfolio


async def test_opens_position_when_signal_and_risk_allow() -> None:
    engine, portfolio = make_engine(FixedSignal(Side.LONG))
    await engine.run_cycle()
    assert [p.side for p in portfolio.state.open_positions] == [Side.LONG]


async def test_does_not_open_when_risk_blocks() -> None:
    engine, portfolio = make_engine(FixedSignal(Side.LONG), can_open=False)
    await engine.run_cycle()
    assert portfolio.state.open_positions == ()


async def test_does_not_open_without_signal() -> None:
    engine, portfolio = make_engine(FixedSignal(None))
    await engine.run_cycle()
    assert portfolio.state.open_positions == ()


async def test_closes_position_when_strategy_says_so() -> None:
    engine, portfolio = make_engine(FixedSignal(Side.SHORT))
    await engine.run_cycle()
    engine.signal = FixedSignal(None, close=True)
    await engine.run_cycle()
    assert portfolio.state.open_positions == ()
