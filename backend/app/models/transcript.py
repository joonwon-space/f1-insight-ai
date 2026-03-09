"""Pydantic models for FIA press conference transcripts."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class SpeakerRole(StrEnum):
    """Role of a speaker in a press conference."""

    DRIVER = "driver"
    TEAM_PRINCIPAL = "team_principal"
    FIA_OFFICIAL = "fia_official"
    JOURNALIST = "journalist"
    OTHER = "other"


class Speaker(BaseModel):
    """A person speaking in a press conference."""

    name: str
    role: SpeakerRole = SpeakerRole.OTHER
    team: str | None = None

    model_config = {"frozen": True}


class Statement(BaseModel):
    """A single statement or answer from a speaker in a press conference."""

    speaker: Speaker
    text: str = Field(description="The spoken content")
    question: str | None = Field(
        default=None,
        description="The question that prompted this statement, if Q&A format",
    )

    model_config = {"frozen": True}


class SessionType(StrEnum):
    """Type of FIA press conference session."""

    DRIVERS = "Drivers Press Conference"
    TEAM_PRINCIPALS = "Team Principals Press Conference"
    POST_QUALIFYING = "Post Qualifying Press Conference"
    POST_RACE = "Post Race Press Conference"
    POST_SPRINT = "Post Sprint Press Conference"
    OTHER = "Other"


class Transcript(BaseModel):
    """A complete parsed FIA press conference transcript."""

    gp_name: str = Field(description="Grand Prix name, e.g. 'Bahrain Grand Prix'")
    session_type: SessionType
    date: datetime | None = None
    statements: list[Statement] = Field(default_factory=list)
    source_url: str
    pdf_filename: str
    raw_text: str = Field(default="", description="Full extracted text before parsing")
    parsed_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"frozen": True}
