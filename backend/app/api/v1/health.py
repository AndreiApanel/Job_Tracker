from app.api.deps import DbSession
from app.schemas.health import HealthResponse
from fastapi import APIRouter
from sqlalchemy import text

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/health/db", response_model=HealthResponse)
async def health_db(db: DbSession) -> HealthResponse:
    await db.execute(text("SELECT 1"))
    return HealthResponse(status="ok")
