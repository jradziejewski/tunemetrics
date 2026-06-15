"""
TuneMetrics – /health Route
-----------------------------
Simple liveness probe – useful for Docker health-checks and load balancers.
"""

from fastapi import APIRouter

from app.config import settings
from app.models import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness check",
    description="Returns `ok` when the API is running.",
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
    )
