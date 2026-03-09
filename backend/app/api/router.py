from fastapi import APIRouter

from app.core.database import ping_mongodb
from app.core.elasticsearch import ping_elasticsearch
from app.scheduler.models import SchedulerStatus
from app.scheduler.service import get_scheduler_status

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint reporting status of all service dependencies."""
    mongodb_ok = await ping_mongodb()
    elasticsearch_ok = await ping_elasticsearch()

    all_healthy = mongodb_ok and elasticsearch_ok
    status = "healthy" if all_healthy else "degraded"

    return {
        "status": status,
        "dependencies": {
            "mongodb": "connected" if mongodb_ok else "disconnected",
            "elasticsearch": "connected" if elasticsearch_ok else "disconnected",
        },
    }


@router.get("/scheduler/status")
async def scheduler_status() -> SchedulerStatus:
    """Return the current scheduler status including mode, next run time, and job count."""
    return get_scheduler_status()
