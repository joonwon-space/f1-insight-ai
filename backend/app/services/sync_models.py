"""Pydantic models for the MongoDB → Elasticsearch sync pipeline."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class SyncMode(StrEnum):
    """Current sync operation mode."""

    IDLE = "idle"
    REALTIME = "realtime"
    FULL = "full"


class SyncStatus(BaseModel):
    """Current state of the sync pipeline."""

    is_running: bool = False
    mode: SyncMode = SyncMode.IDLE
    last_sync_at: datetime | None = None
    error_count: int = 0
    total_synced: int = 0
    last_error: str | None = Field(default=None, description="Most recent error message, if any")
