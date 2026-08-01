from fastapi import APIRouter
from app.db.session import database_status

router = APIRouter(tags=["health"])

@router.get("/health")
@router.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "application": "online",
        "database": database_status(),
    }
