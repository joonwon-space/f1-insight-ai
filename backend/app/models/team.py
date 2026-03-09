"""Pydantic models for F1 teams and drivers."""

from pydantic import BaseModel, Field


class Team(BaseModel):
    """An F1 constructor team."""

    team_id: str = Field(description="Unique identifier, e.g. 'mercedes'")
    name: str = Field(description="Short name, e.g. 'Mercedes'")
    full_name: str = Field(description="Official full name")
    power_unit: str = Field(description="Engine supplier")
    country: str
    team_principal: str
    constructor_id: str = Field(description="Official FIA constructor identifier")

    model_config = {
        "frozen": True,
        "populate_by_name": True,
    }


class Driver(BaseModel):
    """An F1 driver."""

    driver_id: str = Field(description="Unique identifier, e.g. 'hamilton'")
    first_name: str
    last_name: str
    number: int = Field(ge=1, le=99)
    abbreviation: str = Field(max_length=3, description="Three-letter abbreviation, e.g. 'HAM'")
    nationality: str
    team_id: str = Field(description="Reference to Team.team_id")

    model_config = {
        "frozen": True,
        "populate_by_name": True,
    }
