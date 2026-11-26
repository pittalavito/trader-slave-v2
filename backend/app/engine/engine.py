"""Il motore: a ogni ciclo attraversa i livelli in ordine."""

from dataclasses import dataclass

from app.engine.layers import (
    ExecutionLayer,
    MarketDataLayer,
    PortfolioLayer,
    RiskLayer,
    SignalLayer,
    SizingLayer,
)


@dataclass
class BotConfig:
    portfolio_id: int
    symbol: str
    timeframe: str


@dataclass
class Engine:
    config: BotConfig
    market_data: MarketDataLayer
    signal: SignalLayer
    risk: RiskLayer
    sizing: SizingLayer
    execution: ExecutionLayer
    portfolio: PortfolioLayer

    def run_cycle(self) -> None:
        """Un ciclo: prima chiude le posizioni da chiudere, poi valuta un'apertura."""
        cfg = self.config
        market = self.market_data.get(cfg.symbol, cfg.timeframe)
        state = self.portfolio.get(cfg.portfolio_id)

        for position in list(state.open_positions):
            if position.symbol == cfg.symbol and self.signal.should_close(position, market):
                self.execution.close(position, market)
                self.portfolio.record_close(cfg.portfolio_id, position, market)

        state = self.portfolio.get(cfg.portfolio_id)
        if not self.risk.assess(state, market).can_open:
            return

        signal = self.signal.generate(market)
        if signal.side is None:
            return

        order = self.sizing.size(signal, state, market)
        if order is None:
            return

        position = self.execution.open(order, market)
        self.portfolio.record_open(cfg.portfolio_id, position)
