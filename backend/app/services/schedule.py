"""F1 schedule service.

Provides season calendar, session lookup, and current/next session detection.
Tries FastF1 first, falls back to hardcoded data for unavailable seasons.
"""

import logging
from datetime import datetime, timedelta, timezone

from app.models.schedule import (
    CurrentSessionInfo,
    RaceEvent,
    SeasonCalendar,
    Session,
    SessionStatus,
    SessionType,
)
from app.services.fastf1_client import fetch_season_calendar
from app.services.schedule_data_2026 import SEASON_2026, get_fallback_friday

logger = logging.getLogger(__name__)

# In-memory cache keyed by year to avoid repeated lookups
_calendar_cache: dict[int, SeasonCalendar] = {}

# Default session start offsets from the Friday 00:00 UTC anchor
# (day_offset, hour, minute)
_STANDARD_OFFSETS: list[tuple[SessionType, int, int, int]] = [
    (SessionType.FP1, 0, 11, 30),  # Friday 11:30
    (SessionType.FP2, 0, 15, 0),  # Friday 15:00
    (SessionType.FP3, 1, 12, 30),  # Saturday 12:30
    (SessionType.QUALIFYING, 1, 16, 0),  # Saturday 16:00
    (SessionType.RACE, 2, 15, 0),  # Sunday 15:00
]

_SPRINT_OFFSETS: list[tuple[SessionType, int, int, int]] = [
    (SessionType.FP1, 0, 11, 30),  # Friday 11:30
    (SessionType.SPRINT_QUALIFYING, 0, 15, 0),  # Friday 15:00
    (SessionType.SPRINT, 1, 11, 0),  # Saturday 11:00
    (SessionType.QUALIFYING, 1, 15, 0),  # Saturday 15:00
    (SessionType.RACE, 2, 15, 0),  # Sunday 15:00
]

# Duration per session type in minutes
_DURATIONS: dict[SessionType, int] = {
    SessionType.FP1: 60,
    SessionType.FP2: 60,
    SessionType.FP3: 60,
    SessionType.QUALIFYING: 60,
    SessionType.SPRINT_QUALIFYING: 45,
    SessionType.SPRINT: 30,
    SessionType.RACE: 120,
}


def _build_fallback_sessions(
    friday: datetime,
    is_sprint: bool,
) -> list[Session]:
    """Generate sessions for a race weekend from the Friday anchor date."""
    offsets = _SPRINT_OFFSETS if is_sprint else _STANDARD_OFFSETS
    sessions: list[Session] = []
    for stype, day_off, hour, minute in offsets:
        start = friday + timedelta(days=day_off, hours=hour, minutes=minute)
        duration = _DURATIONS.get(stype, 60)
        end = start + timedelta(minutes=duration)
        sessions.append(
            Session(
                session_type=stype,
                start_time=start,
                end_time=end,
                status=SessionStatus.UPCOMING,
            )
        )
    return sessions


def _build_fallback_calendar(year: int) -> SeasonCalendar | None:
    """Build a SeasonCalendar from hardcoded fallback data.

    Currently only 2026 is supported as fallback.
    """
    if year != 2026:
        return None

    events: list[RaceEvent] = []
    for rnd, name, country, circuit, (y, m, d), is_sprint in SEASON_2026:
        friday = get_fallback_friday(y, m, d)
        sessions = _build_fallback_sessions(friday, is_sprint)
        events.append(
            RaceEvent(
                round_number=rnd,
                event_name=name,
                country=country,
                circuit=circuit,
                start_date=sessions[0].start_time,
                end_date=sessions[-1].end_time,
                sessions=sessions,
                is_sprint_weekend=is_sprint,
            )
        )

    return SeasonCalendar(year=year, events=events)


def _apply_statuses(calendar: SeasonCalendar, now: datetime) -> SeasonCalendar:
    """Return a new SeasonCalendar with session statuses set relative to now."""
    updated_events: list[RaceEvent] = []
    for event in calendar.events:
        updated_sessions: list[Session] = []
        for session in event.sessions:
            if now >= session.end_time:
                status = SessionStatus.COMPLETED
            elif now >= session.start_time:
                status = SessionStatus.IN_PROGRESS
            else:
                status = SessionStatus.UPCOMING
            updated_sessions.append(
                Session(
                    session_type=session.session_type,
                    start_time=session.start_time,
                    end_time=session.end_time,
                    status=status,
                )
            )
        updated_events.append(
            RaceEvent(
                round_number=event.round_number,
                event_name=event.event_name,
                country=event.country,
                circuit=event.circuit,
                start_date=event.start_date,
                end_date=event.end_date,
                sessions=updated_sessions,
                is_sprint_weekend=event.is_sprint_weekend,
            )
        )
    return SeasonCalendar(year=calendar.year, events=updated_events)


async def get_season_calendar(year: int) -> SeasonCalendar | None:
    """Get the full season calendar for a given year.

    Attempts FastF1 first, then falls back to hardcoded data.
    Results are cached in memory after the first successful fetch.
    """
    if year in _calendar_cache:
        return _calendar_cache[year]

    calendar = await fetch_season_calendar(year)

    if calendar is None:
        logger.info("FastF1 unavailable for %d, using fallback data", year)
        calendar = _build_fallback_calendar(year)

    if calendar is not None:
        _calendar_cache[year] = calendar

    return calendar


async def get_event_sessions(year: int, round_number: int) -> list[Session] | None:
    """Get all sessions for a specific race event by year and round number."""
    calendar = await get_season_calendar(year)
    if calendar is None:
        return None

    for event in calendar.events:
        if event.round_number == round_number:
            now = datetime.now(tz=timezone.utc)
            updated = _apply_statuses(SeasonCalendar(year=year, events=[event]), now)
            return updated.events[0].sessions

    return None


async def get_current_session_info(
    year: int | None = None,
) -> CurrentSessionInfo:
    """Determine the current in-progress session and/or the next upcoming session.

    If year is None, uses the current UTC year.
    """
    now = datetime.now(tz=timezone.utc)
    if year is None:
        year = now.year

    calendar = await get_season_calendar(year)
    if calendar is None:
        return CurrentSessionInfo()

    calendar = _apply_statuses(calendar, now)

    current_session: Session | None = None
    current_event: RaceEvent | None = None
    next_session: Session | None = None
    next_event: RaceEvent | None = None

    for event in calendar.events:
        for session in event.sessions:
            if session.status == SessionStatus.IN_PROGRESS:
                current_session = session
                current_event = event

            if session.status == SessionStatus.UPCOMING and next_session is None:
                next_session = session
                next_event = event

        # Stop searching once we have both current and next
        if current_session and next_session:
            break
        # If we found a next session but no current one, we can stop too
        if next_session is not None and current_session is None:
            break

    return CurrentSessionInfo(
        current_session=current_session,
        current_event=current_event,
        next_session=next_session,
        next_event=next_event,
    )


def clear_calendar_cache() -> None:
    """Clear the in-memory calendar cache. Useful for testing or forced refresh."""
    _calendar_cache.clear()
