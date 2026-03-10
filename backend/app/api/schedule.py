"""F1 season schedule REST API endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from app.models.schedule import CurrentSessionInfo, SeasonCalendar, Session
from app.services.schedule import get_current_session_info, get_event_sessions, get_season_calendar

router = APIRouter(prefix="/api/schedule", tags=["schedule"])


@router.get("", response_model=SeasonCalendar)
async def get_calendar(
    year: int | None = Query(default=None, description="Season year (defaults to current year)"),
) -> SeasonCalendar:
    """Get the full F1 season calendar for a given year."""
    if year is None:
        year = datetime.now(tz=timezone.utc).year

    calendar = await get_season_calendar(year)
    if calendar is None:
        raise HTTPException(status_code=404, detail=f"Season calendar not found for year {year}")
    return calendar


@router.get("/current", response_model=CurrentSessionInfo)
async def get_current_session() -> CurrentSessionInfo:
    """Get the currently active session and the next upcoming session."""
    return await get_current_session_info()


@router.get("/{round_number}", response_model=list[Session])
async def get_round_sessions(
    round_number: int,
    year: int | None = Query(default=None, description="Season year (defaults to current year)"),
) -> list[Session]:
    """Get all sessions for a specific round."""
    if year is None:
        year = datetime.now(tz=timezone.utc).year

    sessions = await get_event_sessions(year, round_number)
    if sessions is None:
        raise HTTPException(
            status_code=404,
            detail=f"Round {round_number} not found for year {year}",
        )
    return sessions
