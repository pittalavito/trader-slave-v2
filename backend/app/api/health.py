from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.deps import ContainerDep, SessionDep

router = APIRouter()


@router.get("/health")
async def health(container: ContainerDep, session: SessionDep) -> JSONResponse:
    """Used by Docker and the frontend to check that API and database respond."""
    try:
        await session.execute(text("SELECT 1"))
        database = "ok"
    except Exception:
        database = "unreachable"
    ok = database == "ok"
    body = {"status": "ok" if ok else "degraded", "database": database, "env": container.settings.app_env}
    return JSONResponse(status_code=200 if ok else 503, content=body)
