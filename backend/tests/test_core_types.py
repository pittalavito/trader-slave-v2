from decimal import Decimal

import pytest

from app.core.errors import DomainError, ValidationError
from app.core.types import Money, Symbol, Timeframe, TimeframeBlock


def test_money_adds_same_currency() -> None:
    assert Money(Decimal("1.10"), "EUR") + Money(Decimal("2.20"), "EUR") == Money(Decimal("3.30"), "EUR")


def test_money_refuses_mixed_currencies() -> None:
    with pytest.raises(DomainError) as err:
        _ = Money(Decimal("1"), "EUR") + Money(Decimal("1"), "USD")
    assert err.value.code == "currency_mismatch"


def test_money_refuses_floats() -> None:
    with pytest.raises(ValidationError):
        Money(1.5, "EUR")  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        _ = Money(Decimal("1"), "EUR") * 1.5  # type: ignore[operator]


def test_symbol_parse_and_str() -> None:
    assert Symbol.parse("sol/usdc") == Symbol("SOL", "USDC")
    assert str(Symbol("BTC", "USD")) == "BTC/USD"
    with pytest.raises(ValidationError):
        Symbol.parse("BTCUSD")


@pytest.mark.parametrize(
    ("timeframe", "block"),
    [
        (Timeframe.M1, TimeframeBlock.FAST),
        (Timeframe.M3, TimeframeBlock.FAST),
        (Timeframe.M5, TimeframeBlock.MEDIUM),
        (Timeframe.M30, TimeframeBlock.MEDIUM),
        (Timeframe.H1, TimeframeBlock.SLOW),
        (Timeframe.D1, TimeframeBlock.SLOW),
    ],
)
def test_timeframe_blocks(timeframe: Timeframe, block: TimeframeBlock) -> None:
    assert timeframe.block is block


def test_timeframe_seconds() -> None:
    assert Timeframe.M15.seconds == 900
    assert Timeframe.D1.seconds == 86400


def test_production_refuses_default_jwt_secret() -> None:
    from pydantic import ValidationError as PydanticValidationError

    from app.core.config import Settings

    with pytest.raises(PydanticValidationError):
        Settings(app_env="production", _env_file=None)
