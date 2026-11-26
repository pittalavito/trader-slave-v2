"""Il motore: a ogni ciclo attraversa i livelli in ordine.

Lo stesso motore fa backtest, simulazione e soldi veri: cambiano solo i
livelli che riceve (dati storici o in tempo reale, esecuzione simulata o reale).
"""

from dataclasses import dataclass

from app.core.observability import correlation_scope, observed
from app.core.types import PortfolioId, Symbol, Timeframe
from app.engine.layers import (
    ExecutionLayer,
    MarketDataLayer,
    PortfolioLayer,
    RiskLayer,
    SignalLayer,
    SizingLayer,
)


@dataclass(frozen=True, slots=True)
class BotConfig:
    portfolio_id: PortfolioId
    symbol: Symbol
    timeframe: Timeframe


@dataclass
class Engine:
    config: BotConfig
    market_data: MarketDataLayer
    signal: SignalLayer
    risk: RiskLayer
    sizing: SizingLayer
    execution: ExecutionLayer
    portfolio: PortfolioLayer

    @observed(name="engine.run_cycle")
    async def run_cycle(self) -> None:
        """Un ciclo: prima chiude le posizioni da chiudere, poi valuta un'apertura."""
        cfg = self.config
        with correlation_scope(
            portfolio_id=cfg.portfolio_id, symbol=str(cfg.symbol), strategy=self.signal.name
        ):
            market = await self.market_data.get(cfg.symbol, cfg.timeframe)
            state = await self.portfolio.get(cfg.portfolio_id)

            for position in state.open_positions:
                if position.symbol == cfg.symbol and await self.signal.should_close(position, market):
                    await self.execution.close(position, market)
                    await self.portfolio.record_close(cfg.portfolio_id, position, market)

            state = await self.portfolio.get(cfg.portfolio_id)
            if not (await self.risk.assess(state, market)).can_open:
                return

            signal = await self.signal.generate(market)
            if signal.side is None:
                return

            order = await self.sizing.size(signal, state, market)
            if order is None:
                return

            position = await self.execution.open(order, market)
            await self.portfolio.record_open(cfg.portfolio_id, position)
