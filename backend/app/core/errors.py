"""Gerarchia delle eccezioni dell'app.

Ogni eccezione ha un codice stabile (che il frontend può usare) e un messaggio
leggibile. L'API le traduce in risposte HTTP in un solo punto
(`app.api.errors`), e il decoratore `@observed` le registra con il loro codice.
"""

from typing import Any, ClassVar


class AppError(Exception):
    """Base di tutti gli errori previsti dall'app."""

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
    """Un dato in ingresso non è valido."""

    status_code = 422
    default_code = "validation_error"


class AuthenticationError(AppError):
    """Credenziali o token mancanti, scaduti o sbagliati."""

    status_code = 401
    default_code = "authentication_failed"


class PermissionDeniedError(AppError):
    """L'utente è autenticato ma non può fare questa operazione."""

    status_code = 403
    default_code = "permission_denied"


class NotFoundError(AppError):
    """La risorsa richiesta non esiste (o non è visibile all'utente)."""

    status_code = 404
    default_code = "not_found"


class DomainError(AppError):
    """Una regola dell'app è stata violata, per esempio un limite di rischio."""

    status_code = 409
    default_code = "domain_rule_violated"


class ExternalServiceError(AppError):
    """Kraken, Solana, Telegram o un'altra fonte esterna non risponde o rifiuta."""

    status_code = 502
    default_code = "external_service_error"
