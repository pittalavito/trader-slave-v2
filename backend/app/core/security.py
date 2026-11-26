"""Passwords, access tokens and encryption of user secrets."""

from datetime import UTC, datetime, timedelta
from enum import StrEnum

import jwt
from cryptography.fernet import Fernet, InvalidToken
from pwdlib import PasswordHash
from pydantic import BaseModel, ConfigDict

from app.core.clock import Clock
from app.core.errors import AuthenticationError, DomainError
from app.core.types import UserId

_JWT_ALGORITHM = "HS256"


class Role(StrEnum):
    ADMIN = "admin"
    USER = "user"
    OBSERVER = "observer"


class PasswordHasher:
    """Passwords stored with argon2, never in clear text."""

    def __init__(self) -> None:
        self._hasher = PasswordHash.recommended()

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        return self._hasher.verify(password, password_hash)


class TokenPayload(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    user_id: UserId
    role: Role
    expires_at: datetime


class TokenService:
    """Creates and verifies JWT access tokens."""

    def __init__(self, secret: str, expire_minutes: int, clock: Clock) -> None:
        self._secret = secret
        self._expire = timedelta(minutes=expire_minutes)
        self._clock = clock

    def create(self, user_id: UserId, role: Role) -> str:
        now = self._clock.now()
        claims = {"sub": str(user_id), "role": role.value, "iat": now, "exp": now + self._expire}
        return jwt.encode(claims, self._secret, algorithm=_JWT_ALGORITHM)

    def decode(self, token: str) -> TokenPayload:
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=[_JWT_ALGORITHM],
                # Expiry is checked by us with our own clock, so it also works in tests.
                options={"verify_exp": False, "require": ["sub", "role", "exp"]},
            )
            payload = TokenPayload(
                user_id=UserId(int(claims["sub"])),
                role=Role(claims["role"]),
                expires_at=datetime.fromtimestamp(claims["exp"], tz=UTC),
            )
        except (jwt.PyJWTError, ValueError, KeyError) as exc:
            raise AuthenticationError("Invalid token", code="invalid_token") from exc
        if payload.expires_at <= self._clock.now():
            raise AuthenticationError("Token expired", code="token_expired")
        return payload


class SecretBox:
    """Encrypts and decrypts API and wallet keys stored in the database."""

    def __init__(self, key: str | None) -> None:
        self._fernet = Fernet(key.encode()) if key else None

    def _require(self) -> Fernet:
        if self._fernet is None:
            raise DomainError("SECRETS_KEY is not configured: cannot store secrets", code="secrets_key_missing")
        return self._fernet

    def encrypt(self, plaintext: str) -> str:
        return self._require().encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        try:
            return self._require().decrypt(ciphertext.encode()).decode()
        except InvalidToken as exc:
            raise DomainError("Secret cannot be decrypted with the current key", code="secret_undecryptable") from exc
