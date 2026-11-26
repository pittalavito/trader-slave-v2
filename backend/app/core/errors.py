"""App exception hierarchy.

Every exception has a stable code (the frontend can rely on it) and a readable
message. The API turns them into HTTP responses in a single place
(`app.api.errors`), and the `@observed` decorator logs them with their code.
"""

from typing import Any, ClassVar


class AppError(Exception):
    """Base of every expected app error."""

    status_code: ClassVar[int] = 500
    default_code: ClassVar[str] = "internal_error"

    def __init__(self, message: str, *, code: str | None = None, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.code = code or self.default_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class ValidationError(AppError):
    """An input value is not valid."""

    status_code = 422
    default_code = "validation_error"


class AuthenticationError(AppError):
    """Missing, expired or wrong credentials or token."""

    status_code = 401
    default_code = "authentication_failed"


class PermissionDeniedError(AppError):
    """The user is authenticated but not allowed to do this."""

    status_code = 403
    default_code = "permission_denied"


class NotFoundError(AppError):
    """The requested resource does not exist (or is not visible to the user)."""

    status_code = 404
    default_code = "not_found"


class DomainError(AppError):
    """An app rule was broken, for example a risk limit."""

    status_code = 409
    default_code = "domain_rule_violated"


class ExternalServiceError(AppError):
    """Kraken, Solana, Telegram or another external source failed or refused."""

    status_code = 502
    default_code = "external_service_error"
