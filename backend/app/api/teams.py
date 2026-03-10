"""Teams and drivers master data REST API endpoints."""

from fastapi import APIRouter, Query

from app.models.team import Driver, Team
from app.services.repository import MasterDataRepository

router = APIRouter(prefix="/api", tags=["master-data"])


@router.get("/teams", response_model=list[Team])
async def list_teams() -> list[Team]:
    """Return the list of all F1 constructor teams."""
    return await MasterDataRepository.get_teams()


@router.get("/drivers", response_model=list[Driver])
async def list_drivers(
    team: str | None = Query(None, description="Filter drivers by team_id"),
) -> list[Driver]:
    """Return the list of all F1 drivers, optionally filtered by team."""
    drivers = await MasterDataRepository.get_drivers()
    if team:
        drivers = [d for d in drivers if d.team_id == team]
    return drivers
