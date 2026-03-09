"""Pydantic models for F1 schedule data."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class SessionType(StrEnum):
    """F1 session types."""

    FP1 = "FP1"
    FP2 = "FP2"
    FP3 = "FP3"
    QUALIFYING = "Qualifying"
    SPRINT_QUALIFYING = "Sprint Qualifying"
    SPRINT = "Sprint"
    RACE = "Race"


class SessionStatus(StrEnum):
    """Session status relative to current time."""

    UPCOMING = "upcoming"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Session(BaseModel):
    """A single F1 session (practice, qualifying, sprint, or race)."""

    session_type: SessionType
    start_time: datetime
    end_time: datetime
    status: SessionStatus = SessionStatus.UPCOMING

    model_config = {"frozen": True}


class RaceEvent(BaseModel):
    """A single Grand Prix race weekend."""

    round_number: int = Field(ge=1)
    event_name: str
    country: str
    circuit: str
    start_date: datetime
    end_date: datetime
    sessions: list[Session] = Field(default_factory=list)
    is_sprint_weekend: bool = False

    model_config = {"frozen": True}


class SeasonCalendar(BaseModel):
    """Full season calendar containing all race events."""

    year: int
    events: list[RaceEvent]

    model_config = {"frozen": True}


class CurrentSessionInfo(BaseModel):
    """Information about the current and next sessions."""

    current_session: Session | None = None
    current_event: RaceEvent | None = None
    next_session: Session | None = None
    next_event: RaceEvent | None = None
