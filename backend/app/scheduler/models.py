"""Pydantic models for the scheduler module."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class SchedulerMode(StrEnum):
    """Scraping frequency mode."""

    NORMAL = "normal"
    RACE_WEEKEND = "race_weekend"


class SchedulerStatus(BaseModel):
    """Current state of the scheduler."""

    mode: SchedulerMode = SchedulerMode.NORMAL
    is_running: bool = False
    next_run_time: datetime | None = None
    last_run_time: datetime | None = None
    job_count: int = 0
