from datetime import datetime, timezone
from decimal import Decimal

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

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


class FixedMarket(MarketDataLayer):
    def get(self, symbol: str, timeframe: str) -> MarketData:
        price = Decimal("100")
        candle = Candle(symbol, NOW, price, price, price, price, Decimal("1"))
        return MarketData(symbol, timeframe, [candle])


class FixedSignal(SignalLayer):
    name = "fixed"

    def __init__(self, side: Side | None, close: bool = False) -> None:
        self.side = side
        self.close = close

    def generate(self, market: MarketData) -> Signal:
        return Signal(market.symbol, self.side)

    def should_close(self, position: Position, market: MarketData) -> bool:
        return self.close


class FixedRisk(RiskLayer):
    def __init__(self, can_open: bool) -> None:
        self.can_open = can_open

    def assess(self, portfolio: PortfolioState, market: MarketData) -> RiskAssessment:
        return RiskAssessment(self.can_open)


class OneUnitSizing(SizingLayer):
    def size(self, signal: Signal, portfolio: PortfolioState, market: MarketData) -> OrderRequest | None:
        assert signal.side is not None
        return OrderRequest(signal.symbol, signal.side, Decimal("1"), leverage=2)


class PaperExecution(ExecutionLayer):
    def open(self, order: OrderRequest, price_hint: MarketData) -> Position:
        return Position(order.symbol, order.side, order.quantity, price_hint.last_price, order.leverage, NOW)

    def close(self, position: Position, price_hint: MarketData) -> None:
        pass


class MemoryPortfolio(PortfolioLayer):
    def __init__(self) -> None:
        self.state = PortfolioState(portfolio_id=1, capital=Decimal("1000"))

    def get(self, portfolio_id: int) -> PortfolioState:
        return self.state

    def record_open(self, portfolio_id: int, position: Position) -> None:
        self.state.open_positions.append(position)

    def record_close(self, portfolio_id: int, position: Position, exit_price_hint: MarketData) -> None:
        self.state.open_positions.remove(position)


def make_engine(signal: SignalLayer, can_open: bool = True) -> tuple[Engine, MemoryPortfolio]:
    portfolio = MemoryPortfolio()
    engine = Engine(
        config=BotConfig(portfolio_id=1, symbol="SOL/USDC", timeframe="5m"),
        market_data=FixedMarket(),
        signal=signal,
        risk=FixedRisk(can_open),
        sizing=OneUnitSizing(),
        execution=PaperExecution(),
        portfolio=portfolio,
    )
    return engine, portfolio


def test_opens_position_when_signal_and_risk_allow() -> None:
    engine, portfolio = make_engine(FixedSignal(Side.LONG))
    engine.run_cycle()
    assert [p.side for p in portfolio.state.open_positions] == [Side.LONG]


def test_does_not_open_when_risk_blocks() -> None:
    engine, portfolio = make_engine(FixedSignal(Side.LONG), can_open=False)
    engine.run_cycle()
    assert portfolio.state.open_positions == []


def test_does_not_open_without_signal() -> None:
    engine, portfolio = make_engine(FixedSignal(None))
    engine.run_cycle()
    assert portfolio.state.open_positions == []


def test_closes_position_when_strategy_says_so() -> None:
    engine, portfolio = make_engine(FixedSignal(Side.SHORT))
    engine.run_cycle()
    engine.signal = FixedSignal(None, close=True)
    engine.run_cycle()
    assert portfolio.state.open_positions == []
