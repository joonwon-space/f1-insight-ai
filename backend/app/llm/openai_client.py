"""OpenAI-compatible API client.

Works with both cloud OpenAI and local Ollama's /v1/chat/completions endpoint,
enabling seamless switching between local and cloud LLMs.
"""

from __future__ import annotations

import logging

import httpx

from app.llm.models import LLMConfig, LLMResponse, LLMUsage

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT = 120.0


class OpenAIClient:
    """Async client for any OpenAI-compatible chat completions API."""

    def __init__(self, config: LLMConfig) -> None:
        self.base_url = config.base_url.rstrip("/")
        self.default_model = config.model_name
        self.api_key = config.api_key or ""
        self.provider = config.provider

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Generate a chat completion via the OpenAI-compatible API."""
        resolved_model = model or self.default_model
        payload = {
            "model": resolved_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT) as client:
            resp = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]["message"]
        usage_data = data.get("usage", {})

        return LLMResponse(
            content=choice.get("content", ""),
            model=resolved_model,
            provider=self.provider,
            usage=LLMUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
            ),
        )
