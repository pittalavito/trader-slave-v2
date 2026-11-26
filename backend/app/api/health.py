from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Usato da Docker e dal frontend per sapere se l'API risponde."""
    return {"status": "ok", "env": get_settings().app_env}
