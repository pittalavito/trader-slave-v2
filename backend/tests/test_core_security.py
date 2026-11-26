from datetime import timedelta

import pytest
from cryptography.fernet import Fernet

from app.core.clock import SimulatedClock
from app.core.errors import AuthenticationError, DomainError
from app.core.security import PasswordHasher, Role, SecretBox, TokenService
from app.core.types import UserId
from tests.conftest import START


def test_password_hash_roundtrip() -> None:
    hasher = PasswordHasher()
    hashed = hasher.hash("a-password")
    assert hashed != "a-password"
    assert hasher.verify("a-password", hashed)
    assert not hasher.verify("sbagliata", hashed)


def test_token_roundtrip_and_expiry() -> None:
    clock = SimulatedClock(START)
    tokens = TokenService("s" * 32, expire_minutes=60, clock=clock)
    token = tokens.create(UserId(7), Role.OBSERVER)
    payload = tokens.decode(token)
    assert payload.user_id == 7
    assert payload.role is Role.OBSERVER

    clock.advance(timedelta(minutes=61))
    with pytest.raises(AuthenticationError) as err:
        tokens.decode(token)
    assert err.value.code == "token_expired"


def test_token_with_wrong_secret_is_rejected() -> None:
    clock = SimulatedClock(START)
    token = TokenService("u" * 32, 60, clock).create(UserId(1), Role.ADMIN)
    with pytest.raises(AuthenticationError):
        TokenService("d" * 32, 60, clock).decode(token)


def test_secret_box_encrypts() -> None:
    box = SecretBox(Fernet.generate_key().decode())
    cipher = box.encrypt("chiave-api-kraken")
    assert "chiave-api-kraken" not in cipher
    assert box.decrypt(cipher) == "chiave-api-kraken"


def test_secret_box_without_key_refuses() -> None:
    with pytest.raises(DomainError):
        SecretBox(None).encrypt("x")
