"""FastF1 library wrapper for fetching F1 schedule data.

Handles cache setup, schedule retrieval, and graceful fallback
when FastF1 data is unavailable (e.g., future seasons).
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.core.config import settings
from app.models.schedule import (
    RaceEvent,
    SeasonCalendar,
    Session,
    SessionStatus,
    SessionType,
)

logger = logging.getLogger(__name__)

# Default session durations in minutes
_SESSION_DURATIONS: dict[SessionType, int] = {
    SessionType.FP1: 60,
    SessionType.FP2: 60,
    SessionType.FP3: 60,
    SessionType.QUALIFYING: 60,
    SessionType.SPRINT_QUALIFYING: 45,
    SessionType.SPRINT: 30,
    SessionType.RACE: 120,
}


def _init_cache() -> None:
    """Initialize FastF1 cache directory."""
    cache_dir = Path(settings.fastf1_cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    try:
        import fastf1

        fastf1.Cache.enable_cache(str(cache_dir))
        logger.info("FastF1 cache enabled at %s", cache_dir)
    except ImportError:
        logger.warning("FastF1 not installed; cache setup skipped")
    except Exception:
        logger.exception("Failed to enable FastF1 cache")


_cache_initialized = False


def _ensure_cache() -> None:
    """Ensure FastF1 cache is initialized exactly once."""
    global _cache_initialized
    if not _cache_initialized:
        _init_cache()
        _cache_initialized = True


def _session_name_to_type(name: str) -> SessionType | None:
    """Map FastF1 session name strings to SessionType enum."""
    mapping: dict[str, SessionType] = {
        "Practice 1": SessionType.FP1,
        "Practice 2": SessionType.FP2,
        "Practice 3": SessionType.FP3,
        "Qualifying": SessionType.QUALIFYING,
        "Sprint Qualifying": SessionType.SPRINT_QUALIFYING,
        "Sprint Shootout": SessionType.SPRINT_QUALIFYING,
        "Sprint": SessionType.SPRINT,
        "Race": SessionType.RACE,
    }
    return mapping.get(name)


def _build_session(
    session_type: SessionType,
    start_time: datetime,
) -> Session:
    """Build a Session model from a type and start time."""
    duration = _SESSION_DURATIONS.get(session_type, 60)
    end_time = start_time + timedelta(minutes=duration)
    return Session(
        session_type=session_type,
        start_time=start_time,
        end_time=end_time,
        status=SessionStatus.UPCOMING,
    )


def _fetch_season_from_fastf1(year: int) -> SeasonCalendar | None:
    """Attempt to fetch season calendar from FastF1 (blocking call).

    Returns None if FastF1 is unavailable or the season data does not exist.
    """
    _ensure_cache()
    try:
        import fastf1

        schedule = fastf1.get_event_schedule(year, include_testing=False)
    except ImportError:
        logger.warning("FastF1 not installed; cannot fetch schedule")
        return None
    except Exception:
        logger.warning("FastF1 cannot provide %d schedule", year, exc_info=True)
        return None

    if schedule is None or schedule.empty:
        logger.info("FastF1 returned empty schedule for %d", year)
        return None

    events: list[RaceEvent] = []
    for _, row in schedule.iterrows():
        round_number = int(row.get("RoundNumber", 0))
        if round_number < 1:
            continue

        event_name = str(row.get("EventName", ""))
        country = str(row.get("Country", ""))
        circuit = str(row.get("Location", ""))

        sessions: list[Session] = []
        is_sprint = False

        for i in range(1, 6):
            session_key = f"Session{i}"
            date_key = f"Session{i}Date"
            sname = row.get(session_key)
            sdate = row.get(date_key)

            if not sname or not sdate:
                continue

            stype = _session_name_to_type(str(sname))
            if stype is None:
                continue

            if stype in (SessionType.SPRINT, SessionType.SPRINT_QUALIFYING):
                is_sprint = True

            start = sdate
            if hasattr(start, "to_pydatetime"):
                start = start.to_pydatetime()
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)

            sessions.append(_build_session(stype, start))

        if not sessions:
            continue

        sessions.sort(key=lambda s: s.start_time)
        start_date = sessions[0].start_time
        end_date = sessions[-1].end_time

        events.append(
            RaceEvent(
                round_number=round_number,
                event_name=event_name,
                country=country,
                circuit=circuit,
                start_date=start_date,
                end_date=end_date,
                sessions=sessions,
                is_sprint_weekend=is_sprint,
            )
        )

    if not events:
        return None

    events.sort(key=lambda e: e.round_number)
    return SeasonCalendar(year=year, events=events)


async def fetch_season_calendar(year: int) -> SeasonCalendar | None:
    """Fetch season calendar from FastF1, running blocking IO in a thread.

    Returns None if FastF1 data is not available for the given year.
    """
    return await asyncio.to_thread(_fetch_season_from_fastf1, year)
