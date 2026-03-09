"""Ollama REST API client for local LLM inference.

Recommended model: llama3.1:8b (8B params, 4-bit quantized).
Follows the 60/40 memory rule — on a 16 GB machine the model should use ~9-10 GB,
leaving the rest for the OS and application stack.
"""

from __future__ import annotations

import logging

import httpx

from app.llm.models import LLMConfig, LLMProvider, LLMResponse, LLMUsage

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "llama3.1:8b"
_REQUEST_TIMEOUT = 120.0  # seconds — generation can be slow on CPU


class OllamaClient:
    """Async client for the Ollama REST API."""

    def __init__(self, config: LLMConfig) -> None:
        self.base_url = config.base_url.rstrip("/")
        self.default_model = config.model_name or DEFAULT_MODEL

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
        """Generate a completion using the Ollama /api/generate endpoint."""
        resolved_model = model or self.default_model
        payload = {
            "model": resolved_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()

        return LLMResponse(
            content=data.get("response", ""),
            model=resolved_model,
            provider=LLMProvider.OLLAMA,
            usage=LLMUsage(
                prompt_tokens=data.get("prompt_eval_count", 0),
                completion_tokens=data.get("eval_count", 0),
            ),
        )

    # ------------------------------------------------------------------
    # Model management helpers
    # ------------------------------------------------------------------

    async def list_models(self) -> list[str]:
        """Return the list of locally available model names."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                resp.raise_for_status()
                data = resp.json()
            return [m["name"] for m in data.get("models", [])]
        except httpx.HTTPError as exc:
            logger.warning("Failed to list Ollama models: %s", exc)
            return []

    async def check_model_loaded(self, model: str | None = None) -> bool:
        """Check whether a specific model is available locally."""
        resolved = model or self.default_model
        models = await self.list_models()
        return resolved in models

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """Return True if the Ollama server is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(self.base_url)
                return resp.status_code == 200
        except httpx.HTTPError:
            return False
