from fastapi import FastAPI
from httpx import AsyncClient

from app.core.errors import DomainError


async def test_health_checks_database(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok", "env": "test"}


async def test_request_id_is_returned(client: AsyncClient) -> None:
    response = await client.get("/health", headers={"x-request-id": "req-42"})
    assert response.headers["x-request-id"] == "req-42"


async def test_app_errors_become_json_responses(app: FastAPI, client: AsyncClient) -> None:
    @app.get("/boom")
    async def boom() -> None:
        raise DomainError("Leva oltre il tetto", code="leverage_too_high", details={"max": 3})

    response = await client.get("/boom")
    assert response.status_code == 409
    assert response.json() == {
        "error": {"code": "leverage_too_high", "message": "Leva oltre il tetto", "details": {"max": 3}}
    }
