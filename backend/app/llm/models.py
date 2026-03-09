"""Pydantic models for the LLM module."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMUsage(BaseModel):
    """Token usage information from an LLM response."""

    prompt_tokens: int = 0
    completion_tokens: int = 0


class LLMRequest(BaseModel):
    """Request payload for LLM generation."""

    prompt: str
    model: Optional[str] = None
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1, le=32768)


class LLMResponse(BaseModel):
    """Response from an LLM generation call."""

    content: str
    model: str
    provider: LLMProvider
    usage: LLMUsage = Field(default_factory=LLMUsage)


class LLMConfig(BaseModel):
    """Configuration for an LLM provider."""

    provider: LLMProvider
    model_name: str
    base_url: str
    api_key: Optional[str] = None
